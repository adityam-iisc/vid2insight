from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

import raw_data
from agent.config.assistant_config import AssistantConfiguration
from agent.state.agent_state import AgentState
from agent.state.output_state import OutputState
from agent.common.state.input_state import InputState
from agent import nodes, constants
from agent.config.initialize_logger import logger



graph = StateGraph(AgentState,input=InputState, output=OutputState, config_schema=AssistantConfiguration)

graph.add_node(constants.Routes.student_subgraph.value, nodes.student_subgraph)
graph.add_node(constants.Routes.doc_subgraph.value, nodes.doc_subgraph)
graph.add_node(constants.Routes.agent_chat.value, nodes.chat)
graph.add_node(constants.Routes.response_format.value, nodes.format_response)

graph.add_conditional_edges(
    START,
    nodes.agent_router,
    {
        constants.AgentType.student_agent.value: constants.Routes.student_subgraph.value,
        constants.AgentType.doc_agent.value: constants.Routes.doc_subgraph.value,
        constants.AgentType.chat.value: constants.Routes.agent_chat.value
    }
)

graph.add_edge(constants.Routes.student_subgraph.value, constants.Routes.response_format.value)
graph.add_edge(constants.Routes.doc_subgraph.value, constants.Routes.response_format.value)
graph.add_edge(constants.Routes.agent_chat.value, constants.Routes.response_format.value)
graph.add_edge(constants.Routes.response_format.value, END)

checkpointer = InMemorySaver()  # Uncomment if you want to use a checkpointer
app = graph.compile(checkpointer=checkpointer)
app.name = "vid2_insight_graph"
# Uncomment the following lines to visualize the graph
# png_path = "//Users/kumarsa2/Desktop/Personal/vid2insight/agent/imgs/"
# app.get_graph().draw_mermaid_png(output_file_path=png_path + app.name + ".png", max_retries=5, retry_delay=2.0)
# OPENAI_API_KEY="<your-openai-api-key>"
async def main():
    try:
        while True:

            agent_choice = input("enter choice of agent :- chat, student_agent, doc_agent: ")  # Default to doc_chat
            intent = input("enter intent for the agent doc_chat, generate_exec_summary, generate_docs, doc_chat, generate_summary, generate_mcq: " )  # Default to doc_chat
            if agent_choice.lower() == 'exit':
                break
            message = input("Enter your question: ")
            config = {"configurable": {"thread_id": "1", 'agent_choice': agent_choice}}
            context = raw_data.CUMULATIVE_SUMMARY

            payload = {
                "messages": [{"role": "human", "content": message}],
                'expert_preference': agent_choice,
                'video_context': context,
                'intent': intent
            }
            # Note: agent_choice will be removed by _remove_agent_choice in subgraph transitions
            res = await app.ainvoke(payload, config)
            print('---------OUTPUT---------------\n')
            print(res)
            print("-------------CHAT CONTENT---------------\n")
            print(res['chat_content'])
            print("--------------doc_content----------------\n")
            print(res['doc_content'])
    except Exception as e:
        logger.exception(f"Exception in main: {e}", exc_info=True)



if __name__ == "__main__":
    import asyncio
    asyncio.run(main())



