from typing import Dict
import json

from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage
from langchain_core.runnables import RunnableConfig
from narwhals.stable.v1 import exclude
from streamlit.elements.lib.options_selector_utils import maybe_coerce_enum

from agent.config.assistant_config import AssistantConfiguration
from agent.student_agent.constants import MCQResponseModel, SummaryResponseModel
from agent.student_agent.states.agent_state import AgentState
from agent.student_agent import prompts, constants
from agent.config.initialize_logger import logger

from dotenv import load_dotenv

load_dotenv('...')


def load_frame_transcript(state: AgentState, *, config: RunnableConfig) -> dict[str, str]:
    """
    Load the frame transcript from the state.

    Args:
        state (AgentState): The current state of the agent, which includes the transcript and intent.
        config (RunnableConfig): The configuration for the runnable.

    Returns:
        dict[str, str]: A dictionary containing the frame path and transcript.
    """

    logger.info("---LOADING FRAME TRANSCRIPT---")
    # Todo: Read from the frame_transcript_path
    # For now, we will read hardcoded value
    # frame_transcript = raw_data.FRAME_DATA
    frame_transcript = """
            [Intro Slide: 'LangChain: Exploring the Latest Features' appears on screen]
        
        Developer (on camera, smiling):
        'Hey everyone, welcome back to our LangChain deep-dive series. I’m Alex, and today I’m super excited to walk you through some of the newest features in LangChain’s latest release—everything from first-class function calling to enhanced streaming support, and even a brand-new document loader for PDFs. Let’s jump right in!'
        
        [On screen: Title card '1. First-Class Function Calling' fades in]
        
        Alex (voice-over):
        'First up, LangChain now offers first-class function calling. This means you can define functions in Python, register them with your agent, and have the model call those functions directly rather than returning JSON or text you need to parse yourself.'
        
        
        # On screen code snippet:
        from langchain import OpenAI, LLMChain
        from langchain.agents import create_function_agent
        
        def get_weather(city: str) -> str:
            # Dummy implementation
            return f"The weather in {city} is sunny with 68°F."
        
        agent = create_function_agent(
            llm=OpenAI(temperature=0),
            functions=[get_weather]
        )
        
        response = agent.run("What’s the weather like in Tokyo today?")
        print(response)
        Alex (on camera):
        'As you can see here, we define a simple get_weather function, register it, and then call agent.run. LangChain handles converting the model’s intent into an actual function call under the hood—no more manual JSON parsing!'
        
        [On screen: Title card '2. Enhanced Streaming Output']
        
        Alex (voice-over):
        'Next, enhanced streaming. If you’re building chat apps, streaming is a must for that snappy, real-time feel.'
        
        
        # On-screen code snippet:
        from langchain import OpenAI
        from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
        
        llm = OpenAI(streaming=True, callbacks=[StreamingStdOutCallbackHandler()])
        
        result = llm("Tell me a short story about a robot learning to code.")
        Alex (on camera):
        'With streaming=True and the StreamingStdOutCallbackHandler, your application can render tokens as they arrive—perfect for live chat interfaces.'
        
        [On screen: Title card '3. New PDF Document Loader']
        
        Alex (voice-over):
        'Handling PDFs has never been easier. The new PDFLoader automatically extracts text and splits into manageable chunks, ready for embedding or retrieval.'
        
        
        # On-screen code snippet:
        from langchain.document_loaders import PDFLoader
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        
        loader = PDFLoader("whitepaper.pdf")
        docs = loader.load()
        
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        docs = splitter.split_documents(docs)
        Alex (on camera):
        'Just point PDFLoader at your file, split the text using our RecursiveCharacterTextSplitter, and you’re good to go—no manual PDF parsing.'
        
        [On screen: Title card '4. Improved Agent Tools & Plans']
        
        Alex (voice-over):
        'Agents now support customizable tool plans. You can sequence complex chains of tool invocations programmatically.'
        
        
        # On-screen code snippet:
        from langchain.agents import AgentExecutor, Tool
        from langchain import OpenAI
        
        def search_docs(query: str) -> str:
            return "Found relevant docs."
        
        search_tool = Tool(name="search_docs", func=search_docs, description="Search internal docs")
        llm = OpenAI(temperature=0)
        
        agent = AgentExecutor.from_tools(
            tools=[search_tool],
            llm=llm,
            plan_and_execute=True
        )
        
        agent.run("Find information on LangChain’s new memory module.")
        Alex (on camera):
        'This lets you build agents that plan out which tools to call, inspect intermediate results, and adjust on the fly.'
        
        [On screen: Title card '5. Async & Batch Support']
        
        Alex (voice-over):
        'For scalability, LangChain now fully supports async and batch LLM calls, so you can process lots of inputs in parallel.'
        
        
        # On-screen code snippet:
        import asyncio
        from langchain import OpenAI
        
        async def async_request(prompt):
            llm = OpenAI()
            return await llm.apredict(prompt)
        
        prompts = ["Explain recursion", "What is a transformer model?"]
        results = await asyncio.gather(*[async_request(p) for p in prompts])
        print(results)
        Alex (on camera):
        'Use apredict and Python’s asyncio for concurrent requests—ideal for high-throughput services.'
        
        [On screen: 'Wrap-Up & Resources' slide]
        
        Alex (on camera):
        'So those are the highlights: function calling, streaming, PDF loading, smarter agents, and async batching. Check out the GitHub repo for full examples and detailed docs. Don’t forget to star the project, join our Discord, and subscribe for more deep dives. Thanks for watching!'
        
        [End Screen: LangChain logo and 'See you next time!']
    """
    return {
        "transcript": frame_transcript,
        "intent": config['metadata']['intent']
    }


def generate_mcq(state: AgentState, *, config: RunnableConfig) -> dict[str, dict]:
    """
    Generate multiple-choice questions based on the agent's state and configuration.

    Args:
        state (AgentState): The current state of the agent.
        config (RunnableConfig): The configuration for the runnable.

    Returns:
        dict[str, str]: A dictionary containing the generated multiple-choice questions.
    """
    logger.info("---GENERATE MCQ---")

    cfg = AssistantConfiguration.from_runnable_config(config)
    chat_model = cfg.get_model(cfg.default_llm_model)
    additional_messages = state.messages if state.messages[-1] else ''
    cleaned_transcript = state.transcript.replace("\n", "").replace(" ", "")
    cleaned_transcript = " ".join(cleaned_transcript.split())
    messages = [
        SystemMessage(content=prompts.MCQ_GENERATOR_PROMPTS.replace("{context}", cleaned_transcript)),
        HumanMessage(
            content=f"Generate multiple-choice questions based on the provided transcript and on the following custom message {additional_messages}")
    ]
    mcq_doc = chat_model.invoke(messages)

    return {
        "mcq": mcq_doc.content,
        "answer": mcq_doc.content,
        "messages": AIMessage(mcq_doc.content)
    }


def generate_summary(state: AgentState, *, config: RunnableConfig) -> dict[str, str | SummaryResponseModel]:
    """
    Generate a student focussed summary based on the agent's state and configuration.
    :param state: Current state of the agent, including retrieved documents and conversation history.
    :param config: additional configuration for the runnable.
    :return: Output in the form of a dictionary containing the generated summary.
    """
    logger.info("---GENERATING STUDENT SUMMARY---")

    cfg = AssistantConfiguration.from_runnable_config(config)
    chat_model = cfg.get_model(cfg.default_llm_model)
    cleaned_transcript = state.transcript.replace("\n", "").replace(" ", "")
    cleaned_transcript = " ".join(cleaned_transcript.split())
    additional_messages = state.messages if state.messages[-1] else ''
    messages = [
        SystemMessage(content=prompts.STUDENT_SUMMARY_PLAN.replace("{context}", cleaned_transcript)),
        HumanMessage(content="Generate a student summary and plan on the provided transcript")
    ]
    summary_plan = chat_model.invoke(messages)

    return {
        "summary": summary_plan.content,
        "answer": summary_plan.content,
        "messages": AIMessage(summary_plan.content)
    }


def decide_intent(state: AgentState, *, config: RunnableConfig) -> str:
    """
    Decide the intent based on the agent's state and configuration.

    Args:
        state (AgentState): The current state of the agent.
        config (RunnableConfig): The configuration for the runnable.

    Returns:
        dict[str, str]: A dictionary containing the decided intent.

    Raises:
        ValueError: If the intent is not found in the state.
    """
    try:
        logger.debug("---DECIDE INTENT---")
        # Check if 'intent' is in the state
        if state.intent.lower() != '':
            return state.intent
        else:
            raise ValueError("Intent not found in state")
    except Exception as e:
        logger.exception(f"Error deciding intent: {e}", exc_info=True)
        raise


def chat(state: AgentState, *, config: RunnableConfig) -> dict[str, BaseMessage | list[BaseMessage]]:
    """
    Generate a response to the user's query based on the data.

    Args:
        state (AgentState): The current state of the agent, including retrieved documents and conversation history.
        config (RunnableConfig): The configuration for the runnable.

    Returns:
        dict[str, list[str]]: A dictionary with a 'messages' key containing the generated response.
    """
    logger.debug("---CHAT---")

    configuration = AssistantConfiguration.from_runnable_config(config)
    chat_model = configuration.get_model(configuration.default_llm_model)
    cleaned_transcript = state.transcript.replace("\n", "").replace(" ", "")
    cleaned_transcript = " ".join(cleaned_transcript.split())
    if len(state.messages) == 1:
        messages = [
                       SystemMessage(
                           content=prompts.CHAT_SYSTEM_PROMPT.replace("{context}", cleaned_transcript)
                       )
                   ] + state.messages
    else:
        messages = [
            state.messages
        ]
    response = chat_model.invoke(messages)

    return {"messages": [response.content],
            "answer": response.content
        }


def evaluate(state: AgentState, *, config: RunnableConfig) -> Dict[str, str | int]:
    """
    Evaluate the last response and decide if modification is required.
    """
    try:
        logger.info("---EVALUATE---")
        cfg = AssistantConfiguration.from_runnable_config(config)
        chat_model = cfg.get_model(cfg.default_llm_model).with_structured_output(constants.EvaluatorResponseModel)

        if state.intent == constants.Intent.GENERATE_MCQ.value:
            data = state.answer
        elif state.intent == constants.Intent.GENERATE_SUMMARY.value:
            data = state.answer
        else:
            raise ValueError(f"Unsupported intent for evaluation: {state.intent}")

        messages = [SystemMessage(content=prompts.EVALUATOR_PROMPT.replace("{context}", data))] + state.messages
        response = chat_model.invoke(messages)

        return {
            "is_modification_required": response.is_modification_required,
            "feedback": response.feedback,
            "turn": state.turn + 1,
            "answer": state.messages[-1],
            "messages": HumanMessage(f"feedback: {response.feedback}")
        }
    except Exception as exc:
        logger.exception(f"Exception in evaluate: {exc}")
        raise


def decide_modification(state: AgentState, *, config: RunnableConfig) -> str:
    """
    Decide whether to loop back for another modification or end.
    """
    try:
        logger.info("---DECIDE MODIFICATION---")
        if state.turn >= 3:
            return constants.Routes.END.value
        if state.is_modification_required:
            return state.intent
        return constants.Routes.END.value
    except Exception as exc:
        logger.exception(f"Exception in decide_modification: {exc}")
        raise
