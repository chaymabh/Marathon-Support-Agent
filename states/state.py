from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from typing import Dict, List, Any

class AgentGraphState(TypedDict):
    question: str
    user: str
    selected_tools: str
    planner_responce: Annotated[list, add_messages]
    get_events_responce: Annotated[list, add_messages]
    get_tickets_responce: Annotated[list, add_messages]
    get_customers_responce: Annotated[list, add_messages]
    get_faq_responce: Annotated[list, add_messages]
    get_orders_responce: Annotated[list, add_messages]
    summerization_agent_responce: Annotated[list, add_messages]
    #edesk_tool_responce: Annotated[list, add_messages]
    reporter_responce: Annotated[list, add_messages]
    final_reports: Annotated[list, add_messages]
    end_chain: Annotated[list, add_messages]
    
def get_agent_graph_state(state: AgentGraphState, state_key: str) -> Any:
    if  state_key == "planner_latest":
        if state["planner_responce"]:
            return state["planner_responce"][-1]
        else:
            return state["planner_responce"]
    
    # if  state_key == "edesk_tool_latest":
    #     if state["edesk_tool_responce"]:
    #         return state["edesk_tool_responce"][-1]
    #     else:
    #         return state["edesk_tool_responce"]
    
    if state_key == "knowledge_base":
        tools_responces = {
            "get_events_responce": state["get_events_responce"],
            "get_tickets_responce": state["get_tickets_responce"],
            "get_customers_responce": state["get_customers_responce"],
            "get_orders_responce": state["get_orders_responce"],
            "get_faq_responce": state["get_faq_responce"],
        }
        return {key: response for key, response in tools_responces.items() if response}
    
state = { 
    "question":"",
    "user":"",
    "selected_tools":"",
    "planner_responce": [],
    "get_events_responce":[],
    "get_tickets_responce":[],
    "get_customers_responce":[],
    "get_orders_responce":[],
    "get_faq_responce":[],
    "summerization_agent_responce":[],
    #"edesk_tool_responce":[],
    "reporter_responce": [],
    "end_chain": []
}