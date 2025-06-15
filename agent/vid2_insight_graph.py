from langgraph.graph import END, START, StateGraph

from agent.config.assistant_config import AssistantConfiguration
from agent.state.agent_state import AgentState
from agent.state.output_state import OutputState
from agent.common.state.input_state import InputState



graph = StateGraph(AgentState,input=InputState, output=OutputState, config_schema=AssistantConfiguration)
