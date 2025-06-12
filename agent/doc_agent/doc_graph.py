import asyncio

from langgraph.graph import StateGraph, START, END

from agent.config.assistant_config import AssistantConfiguration
from agent.config.initialize_logger import logger
from agent.doc_agent import nodes, constants
from agent.doc_agent.state.agent_state import AgentState
from agent.doc_agent.state.input_state import InputState
from agent.doc_agent.state.output_state import OutputState

graph = StateGraph(AgentState, input=InputState, output=OutputState, config_schema=AssistantConfiguration)

graph.add_node(constants.Routes.CONTEXT.value, nodes.load_frame_transcript)

graph.add_node(constants.Routes.EXECUTIVE_SUMMARY.value, nodes.generate_executive_summary)

graph.add_node(constants.Routes.PRODUCT_DOCUMENTS.value, nodes.generate_product_document)

graph.add_node(constants.Routes.DOC_CHAT.value, nodes.chat)

graph.add_edge(START, constants.Routes.CONTEXT.value)
graph.add_conditional_edges(constants.Routes.CONTEXT.value, nodes.decide_intent,
                            {
                                constants.Intent.GENERATE_EXEC_SUMMARY.value: constants.Routes.EXECUTIVE_SUMMARY.value,
                                constants.Intent.GENERATE_DOCS.value: constants.Routes.PRODUCT_DOCUMENTS.value,
                                constants.Intent.DOC_CHAT.value: constants.Routes.DOC_CHAT.value,
                            }
                            )

graph.add_edge(constants.Routes.EXECUTIVE_SUMMARY.value, END)
graph.add_edge(constants.Routes.PRODUCT_DOCUMENTS.value, END)
graph.add_edge(constants.Routes.DOC_CHAT.value, END)
app = graph.compile()
app.name = "doc_agent"


# png_path="/Users/kumarsa2/Desktop/Personal/vid2insight/agent/doc_agent/imgs/"
# app.get_graph().draw_mermaid_png(output_file_path=png_path+app.name+".png")
async def main():
    config = {"configurable": {"thread_id": "1", "user_id": "kumarsa2", 'intent': 'generate_exec_summary',
                               'file_path': '/Users/kumarsa2/Downloads/abc.mp4'}}
    input = {"messages": [{"role": "human", "content": "tell me about the video"}]}

    try:
        res = await app.ainvoke(input, config)
        print('---------OUTPUT---------------\n')
        print(res)

        print('---------OUTPUT---------------\n')
        print(res['answer'])
    except Exception as e:
        logger.error("An error occurred while invoking ainvoke:", exc_info=True)


# Run the async main function
if __name__ == "__main__":
    asyncio.run(main())
    pass
