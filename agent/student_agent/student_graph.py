import asyncio

from langgraph.graph import StateGraph,START, END

# import raw_data
from agent.config.assistant_config import AssistantConfiguration
from agent.student_agent.states.agent_state import AgentState
from agent.student_agent import nodes, constants
from agent.common.state.input_state import InputState
from agent.student_agent.states.output_state import OutputState
from langgraph.checkpoint.memory import InMemorySaver
from agent.config.initialize_logger import logger


graph = StateGraph(AgentState,input=InputState, output=OutputState, config_schema=AssistantConfiguration)

graph.add_node(constants.Routes.CONTEXT.value, nodes.initialize_context)
graph.add_node(constants.Routes.MCQ.value, nodes.generate_mcq)
graph.add_node(constants.Routes.EVALUATOR.value, nodes.evaluate)
graph.add_node(constants.Routes.SUMMARY.value, nodes.generate_summary)
graph.add_node(constants.Routes.CHAT.value, nodes.chat)

# Edges
graph.add_edge(START, constants.Routes.CONTEXT.value)
graph.add_conditional_edges(
    constants.Routes.CONTEXT.value,
    nodes.decide_intent,
    {
        constants.Intent.GENERATE_MCQ.value: constants.Routes.MCQ.value,
        constants.Intent.GENERATE_SUMMARY.value: constants.Routes.SUMMARY.value,
        constants.Intent.DOC_CHAT.value: constants.Routes.CHAT.value
    }
)
graph.add_edge(constants.Routes.MCQ.value, constants.Routes.EVALUATOR.value)
graph.add_edge(constants.Routes.SUMMARY.value, constants.Routes.EVALUATOR.value)
graph.add_edge(constants.Routes.CHAT.value, END)
graph.add_conditional_edges(
    constants.Routes.EVALUATOR.value,
    nodes.decide_modification,
    {
        constants.Intent.GENERATE_MCQ.value: constants.Routes.MCQ.value,
        constants.Intent.GENERATE_SUMMARY.value: constants.Routes.SUMMARY.value,
        'end': END
    }
)



checkpointer = InMemorySaver()
app = graph.compile(checkpointer=checkpointer)
app.name = "student_agent"



# png_path="/Users/admukhop/Desktop/iisc/Deep Learning/project/vid2insight/agent/imgs/"
# app.get_graph().draw_mermaid_png(output_file_path=png_path+app.name+".png",max_retries=5, retry_delay=2.0, draw_method=MermaidDrawMethod.PYPPETEER)
# async def main():
#     try:
#        while True:
#            #generate_exec_summary
#            intent = input("Enter intent (generate_mcq, generate_summary, doc_chat) or 'exit' to quit: ")
#            message = input("Enter message: ")
#            config = {"configurable": {"thread_id": "1", "user_id": "kumarsa2", 'intent': intent,
#                                       'file_path': '/Users/kumarsa2/Downloads/abc.mp4'}}
#            context = raw_data.frame_transcript
#
#            payload = {"messages": [{"role": "human", "content": message}], 'intent': intent, 'video_context': context}
#            res = await app.ainvoke(payload, config)
#            print('---------OUTPUT---------------\n')
#            print(res['answer'])
#
#     except Exception as e:
#         logger.error("An error occurred while invoking ainvoke:", exc_info=True)
# # # Run the async main function
# if __name__ == "__main__":
#     asyncio.run(main())
#     pass