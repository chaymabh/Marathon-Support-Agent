import os
import json
import requests
from sqlalchemy import create_engine, MetaData, Table, select
from dotenv import load_dotenv
from states.state import AgentGraphState
from langchain_core.messages import HumanMessage
from langchain.tools import Tool
from pydantic import BaseModel, Field
from utils.logger import logger
from utils.helper_functions import serialize_record, CustomJSONEncoder

load_dotenv()

EDESK_API_URL = os.getenv("EDESK_API_URL")
EDESK_API_KEY = os.getenv("EDESK_API_KEY")
DATABASE_URI = os.getenv("DATABASE_URI")
 
engine = create_engine(DATABASE_URI, echo=False)

metadata = MetaData()

metadata.reflect(bind=engine)

events_table = metadata.tables['events']
tickets_table = metadata.tables['tickets']
customers_table = metadata.tables['customers']
orders_table = metadata.tables['orders']
faq_table = metadata.tables['faq']

class TicketCreationInput(BaseModel):
    subject: str = Field(..., description="Subject of the ticket")
    description: str = Field(..., description="Description of the issue")
    priority: str = Field(default="medium", description="Priority of the ticket")
    requester_email: str = Field(default="admin@gmail.com", description="Email of the requester")

def edesk_tool(state: AgentGraphState):
   
    agent_response = state.get("summarization_agent_responce", {})

    subject = agent_response.get("subject", "No Subject")
    description = agent_response.get("description", "No Description")
    priority = agent_response.get("priority", "medium")

    customer = agent_response.get("customer", {})
    requester_name = customer.get("name", "unknown")
    requester_email = customer.get("email", "unknown")

    tags = agent_response.get("tags", [])

    payload = {
        "subject": subject,
        "description": description,
        "priority": priority,
        "requester": {
            "name": requester_name,
            "email": requester_email
        },
        "tags": tags
    }

    if not EDESK_API_URL or not EDESK_API_KEY:
        return {"error": "Missing EDESK_API_URL or EDESK_API_KEY in environment variables."}

    headers = {
        "Authorization": f"Bearer {EDESK_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(EDESK_API_URL, json=payload, headers=headers)
        response.raise_for_status()
         
        state["edesk_tool_responce"] = [HumanMessage(role="system", content=json.dumps(response.json(), cls=CustomJSONEncoder))]
            
        return {"edesk_tool_responce": state["edesk_tool_responce"]}
    
    except requests.RequestException as e:
        error_mgs= {"error": str(e), "payload": payload}
        state["edesk_tool_responce"] = [HumanMessage(role="system", content=json.dumps(error_mgs, cls=CustomJSONEncoder))]
            
        return {"edesk_tool_responce": state["edesk_tool_responce"]}

def knowledge_base_tool(state: AgentGraphState):
    state["selected_tools"] = [HumanMessage(role="system", content="yes")]
    logger.debug("Successfully opened knowledge base.")
    return {"selected_tools": state["selected_tools"]}
    
def get_events(state: AgentGraphState):
    try:
        logger.debug("Fetching events from the database.")
        with engine.connect() as connection:
            result = connection.execute(select(events_table))
            events = [serialize_record(row) for row in result]
            state["get_events_responce"] = [HumanMessage(role="system", content=json.dumps(events, cls=CustomJSONEncoder))]
            logger.debug("Successfully fetched events.")
            return {"get_events_responce": state["get_events_responce"]}
    except Exception as e:
        logger.error(f"Error fetching events: {e}")
        return {"get_events_responce": [HumanMessage(role="system", content=json.dumps({"error": str(e)}, cls=CustomJSONEncoder))]}

def get_tickets(state: AgentGraphState):
    try:
        logger.debug("Fetching tickets from the database.")
        with engine.connect() as connection:
            result = connection.execute(select(tickets_table))
            tickets = [serialize_record(row) for row in result]
            state["get_tickets_responce"] = [HumanMessage(role="system", content=json.dumps(tickets, cls=CustomJSONEncoder))]
            logger.debug("Successfully fetched tickets.")
            return {"get_tickets_responce": state["get_tickets_responce"]}
    except Exception as e:
        logger.error(f"Error fetching tickets: {e}")
        return {"get_tickets_responce": [HumanMessage(role="system", content=json.dumps({"error": str(e)}, cls=CustomJSONEncoder))]}

def get_customers(state: AgentGraphState):
    try:
        logger.debug("Fetching customers from the database.")
        with engine.connect() as connection:
            result = connection.execute(select(customers_table))
            customers = [serialize_record(row) for row in result]
            state["get_customers_responce"] = [HumanMessage(role="system", content=json.dumps(customers, cls=CustomJSONEncoder))]
            logger.debug("Successfully fetched customers.")
            return {"get_customers_responce": state["get_customers_responce"]}
    except Exception as e:
        logger.error(f"Error fetching customers: {e}")
        return {"get_customers_responce": [HumanMessage(role="system", content=json.dumps({"error": str(e)}, cls=CustomJSONEncoder))]}

def get_orders(state: AgentGraphState):
    try:
        logger.debug("Fetching orders from the database.")
        with engine.connect() as connection:
            result = connection.execute(select(orders_table))
            orders = [serialize_record(row) for row in result]
            state["get_orders_responce"] = [HumanMessage(role="system", content=json.dumps(orders, cls=CustomJSONEncoder))]
            logger.debug("Successfully fetched orders.")
            return {"get_orders_responce": state["get_orders_responce"]}
    except Exception as e:
        logger.error(f"Error fetching orders: {e}")
        return {"get_orders_responce": [HumanMessage(role="system", content=json.dumps({"error": str(e)}, cls=CustomJSONEncoder))]}

def get_faq(state: AgentGraphState):
    try:
        logger.debug("Fetching FAQs from the database.")
        with engine.connect() as connection:
            result = connection.execute(select(faq_table))
            faqs = [serialize_record(row) for row in result]
            state["get_faq_responce"] = [HumanMessage(role="system", content=json.dumps(faqs, cls=CustomJSONEncoder))]
            logger.debug("Successfully fetched FAQs.")
            return {"get_faq_responce": state["get_faq_responce"]}
    except Exception as e:
        logger.error(f"Error fetching FAQs: {e}")
        return {"get_faq_responce": [HumanMessage(role="system", content=json.dumps({"error": str(e)}, cls=CustomJSONEncoder))]}

# Create tools
tools = [
    Tool.from_function(
        func=edesk_tool,
        name="edesk_tool",
        description="Creates a helpdesk ticket using information extracted from the AgentGraphState.",
    ),
    
    Tool.from_function(
        func=knowledge_base_tool,
        name="knowledge_base_tool",
        description="Knowledge base",
        return_direct=True,
    ),
    Tool.from_function(
        func=get_events,
        name="get_events",
        description="Fetch all events from the database.",
        return_direct=True,
    ),
    Tool.from_function(
        func=get_tickets,
        name="get_tickets",
        description="Fetch all tickets from the database.",
        return_direct=True,
    ),
    Tool.from_function(
        func=get_customers,
        name="get_customers",
        description="Fetch all customers from the database.",
        return_direct=True,
    ),
    Tool.from_function(
        func=get_orders,
        name="get_orders",
        description="Fetch all orders from the database.",
        return_direct=True,
    ),
    Tool.from_function(
        func=get_faq,
        name="get_faq",
        description="Fetch all FAQs from the database.",
        return_direct=True,
    ),
]
