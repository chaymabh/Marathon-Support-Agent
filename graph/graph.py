import json
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage
from states.state import AgentGraphState, get_agent_graph_state, state
from agents.agents import (
    PlannerAgent,
    SummerizationAgent,
    ReporterAgent,
    EndNodeAgent
)
from tools.data_tools import tools
from prompts.prompts import (
    planner_prompt_template,
    reporter_prompt_template,
    summarization_agent_prompt_template,
    planner_guided_json,
    summerization_agent_guided_json,
    reporter_guided_json,
)
from langgraph.checkpoint.memory import MemorySaver
from typing import Hashable, List
from utils.logger import logger

def create_graph(server=None, model=None, stop=None, model_endpoint=None, temperature=0, memory=MemorySaver()):
    logger.debug("Creating graph with parameters: server={}, model={}, stop={}, model_endpoint={}, temperature={}".format(server, model, stop, model_endpoint, temperature))

    def tools_list(state: AgentGraphState) -> List[Hashable]:
        logger.debug("Extracting tools list from state.")
        agent_responces = {
            "planner_responce": state.get("planner_responce", []),
        }
        tool_names = []

        for agent, planner_responce in agent_responces.items():
            if isinstance(planner_responce, list):
                for item in planner_responce:
                    if isinstance(item, HumanMessage):
                        json_str = item.content
                        item_dict = json.loads(json_str)
                        tools_to_use = item_dict.get("tools_to_use", [])

                        if isinstance(tools_to_use, str):
                            tools_to_use = tools_to_use.split(', ')

                        tool_names.extend(tools_to_use)
        logger.debug("Tools list extracted: {}".format(tool_names))
        return tool_names

    graph = StateGraph(AgentGraphState)
    logger.debug("StateGraph initialized.")

    graph.add_node(
        "planner",
        lambda state: PlannerAgent(
            state=state,
            model=model,
            server=server,
            guided_json=planner_guided_json,
            stop=stop,
            model_endpoint=model_endpoint,
            temperature=temperature
        ).invoke(
            question=state["question"],
            prompt=planner_prompt_template,
            memory=memory
        )
    )
    logger.debug("Added 'planner' node to the graph.")

    tools_dict = {tool.name: tool.func for tool in tools}
    logger.debug("Tools dictionary created: {}".format(tools_dict.keys()))

    for tool_name, tool_func in tools_dict.items():
        graph.add_node(
            tool_name,
            lambda state, func=tool_func: func(state=state)
        )
        logger.debug("Added tool node '{}' to the graph.".format(tool_name))

    graph.add_node(
        "summerization_agent",
        lambda state: SummerizationAgent(
            state=state,
            model=model,
            server=server,
            guided_json=summerization_agent_guided_json,
            stop=stop,
            model_endpoint=model_endpoint,
            temperature=temperature
        ).invoke(
            question=state["question"],
            email=state["user_id"],
            state=state,
            prompt=summarization_agent_prompt_template,
        )
    )
    logger.debug("Added 'summerization_agent' node to the graph.")

    graph.add_node(
        "reporter",
        lambda state: ReporterAgent(
            state=state,
            model=model,
            server=server,
            stop=stop,
            guided_json=reporter_guided_json,
            model_endpoint=model_endpoint,
            temperature=temperature
        ).invoke(
            question=state["question"],
            knowledge_base=get_agent_graph_state(state=state, state_key="knowledge_base"),
            edesk_tool=get_agent_graph_state(state=state, state_key="edesk_tool_latest"),
            planner=get_agent_graph_state(state=state, state_key="planner_latest"),
            prompt=reporter_prompt_template,
            memory=memory
        )
    )
    logger.debug("Added 'reporter' node to the graph.")

    graph.add_node("end", lambda state: EndNodeAgent(state).invoke())
    logger.debug("Added 'end' node to the graph.")

    def planner_to_execution_agent(state: AgentGraphState):
        logger.debug("Determining next agent from planner response.")
        agent_list = state["planner_responce"]
        if agent_list:
            agent = agent_list[-1]
        else:
            agent = "No agent"

        if agent != "No agent":
            if isinstance(agent, HumanMessage):
                agent_content = agent.content
            else:
                agent_content = agent

            agent_data = json.loads(agent_content)
            next_agent = agent_data["next_agent"]
        else:
            next_agent = "summerization_agent"

        logger.debug("Next agent determined: {}".format(next_agent))
        return next_agent

    def connect_agent_to_tools(state: AgentGraphState) -> str:
     logger.debug("Connecting agent to tools.")
     selected_tools = tools_list(state)
     valid_tools = [tool for tool in selected_tools if tool in tools_dict]
     if valid_tools:
        logger.debug("Valid tools selected: {}".format(valid_tools))
        return valid_tools[0]  # Return the first valid tool
     logger.debug("No valid tools selected. Using 'selector'.")
     return "selector"

    graph.set_entry_point("planner")
    graph.set_finish_point("end")
    logger.debug("Graph entry and finish points set.")

    graph.add_conditional_edges(
        source="planner",
        path=planner_to_execution_agent,
    )
    logger.debug("Added conditional edges from 'planner'.")

    graph.add_edge("summerization_agent", "edesk_tool")
    logger.debug("Added edge from 'summerization_agent' to 'edesk_tool'.")

    graph.add_conditional_edges(
        source="knowledge_base_tool",
        path=connect_agent_to_tools,
    )
    
    logger.debug("Added conditional edges from 'knowledge_base_tool'.")
    
    for tool_name, tool_func in tools_dict.items():
      if tool_name != "knowledge_base_tool":
        graph.add_edge(tool_name, "reporter")
        logger.debug("Added edge from tool '{}' to 'reporter'.".format(tool_name))

    graph.add_edge("reporter", "end")

    return graph

def compile_workflow(graph, memory):
    logger.debug("Compiling workflow.")
    workflow = graph.compile(checkpointer=memory)
    logger.debug("Workflow compiled successfully.")
    return workflow
