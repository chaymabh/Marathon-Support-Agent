import os
import json
import logging
import requests
from decimal import Decimal
from datetime import date, time, datetime
from sqlalchemy import create_engine, MetaData, Table, select
from dotenv import load_dotenv
from states.state import AgentGraphState
from langchain_core.messages import HumanMessage
from langchain.tools import Tool
from pydantic import BaseModel, Field
from utils.logger import logger

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the database URI from environment variables
DATABASE_URI = "postgresql+psycopg2://postgres:password123123A@localhost:5432/client_db"

# Create a synchronous engine with echo set to False to suppress SQL logs
engine = create_engine(DATABASE_URI, echo=False)

# Create a MetaData instance
metadata = MetaData()

# Reflect the tables from the database
metadata.reflect(bind=engine)

# Access tables
events_table = metadata.tables['events']
tickets_table = metadata.tables['tickets']
customers_table = metadata.tables['customers']
orders_table = metadata.tables['orders']
faq_table = metadata.tables['faq']

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, (date, time, datetime)):
            return obj.isoformat()
        return super().default(obj)

def serialize_record(row):
    record = dict(row._mapping)
    return json.loads(json.dumps(record, cls=CustomJSONEncoder))

# Define a model for the input parameters
class TicketCreationInput(BaseModel):
    subject: str = Field(..., description="Subject of the ticket")
    description: str = Field(..., description="Description of the issue")
    priority: str = Field(default="medium", description="Priority of the ticket")
    requester_email: str = Field(default="requester@example.com", description="Email of the requester")

# Get API details from environment variables
HELPDESK_API_URL = os.getenv("HELPDESK_API_URL")
HELPDESK_API_KEY = os.getenv("HELPDESK_API_KEY")

def extract_ticket_info_from_state(state: AgentGraphState):
    #logger.debug("Extracting ticket information from state.")
    agent_responce = state.get("summarization_agent_responce", {})
    subject = agent_responce.get("subject", "No Subject")
    description = agent_responce.get("description", "No Description")
    priority = agent_responce.get("priority", "medium")
    requester_email = agent_responce.get("requester_email", "requester@example.com")

    #logger.debug(f"Extracted ticket info: subject={subject}, description={description}, priority={priority}, requester_email={requester_email}")
    return {
        "subject": subject,
        "description": description,
        "priority": priority,
        "requester_email": requester_email
    }

# def edesk_tool(state: AgentGraphState) -> str:
#     #logger.debug("Starting edesk_tool function.")
#     ticket_info = extract_ticket_info_from_state(state)
#     headers = {
#         "Content-Type": "application/json",
#         "Authorization": f"Bearer {HELPDESK_API_KEY}"
#     }
#     data = {
#         "ticket": {
#             "subject": ticket_info["subject"],
#             "description": ticket_info["description"],
#             "priority": ticket_info["priority"],
#             "requester_email": ticket_info["requester_email"]
#         }
#     }

#     #logger.debug("Sending request to create ticket.")
#     response = requests.post(HELPDESK_API_URL, headers=headers, json=data)

#     if response.status_code == 201:
#         result = f"Ticket created successfully! Ticket ID: {response.json().get('ticket', {}).get('id')}"
#         state["edesk_tool_responce"] = [HumanMessage(role="system", content=json.dumps(result, cls=CustomJSONEncoder))]
#         #logger.debug("Ticket created successfully.")
#         return {"edesk_tool_responce": state["edesk_tool_responce"]}
#     else:
#         result = f"Failed to create ticket. Status Code: {response.status_code}, Response: {response.text}"
#         state["edesk_tool_responce"] = [HumanMessage(role="system", content=json.dumps(result, cls=CustomJSONEncoder))]
#         logger.error(result)
#         return {"edesk_tool_responce": state["edesk_tool_responce"]}

def knowledge_base_tool(state: AgentGraphState):
    state["selected_tools"] = [HumanMessage(role="system", content="yes")]
    #logger.debug("Successfully fetched events.")
    return {"selected_tools": state["selected_tools"]}
    
def get_events(state: AgentGraphState):
    try:
        #logger.debug("Fetching events from the database.")
        with engine.connect() as connection:
            result = connection.execute(select(events_table))
            events = [serialize_record(row) for row in result]
            state["get_events_responce"] = [HumanMessage(role="system", content=json.dumps(events, cls=CustomJSONEncoder))]
            #logger.debug("Successfully fetched events.")
            return {"get_events_responce": state["get_events_responce"]}
    except Exception as e:
        logger.error(f"Error fetching events: {e}")
        return {"get_events_responce": [HumanMessage(role="system", content=json.dumps({"error": str(e)}, cls=CustomJSONEncoder))]}

def get_tickets(state: AgentGraphState):
    try:
        #logger.debug("Fetching tickets from the database.")
        with engine.connect() as connection:
            result = connection.execute(select(tickets_table))
            tickets = [serialize_record(row) for row in result]
            state["get_tickets_responce"] = [HumanMessage(role="system", content=json.dumps(tickets, cls=CustomJSONEncoder))]
            #logger.debug("Successfully fetched tickets.")
            return {"get_tickets_responce": state["get_tickets_responce"]}
    except Exception as e:
        logger.error(f"Error fetching tickets: {e}")
        return {"get_tickets_responce": [HumanMessage(role="system", content=json.dumps({"error": str(e)}, cls=CustomJSONEncoder))]}

def get_customers(state: AgentGraphState):
    try:
        #logger.debug("Fetching customers from the database.")
        with engine.connect() as connection:
            result = connection.execute(select(customers_table))
            customers = [serialize_record(row) for row in result]
            state["get_customers_responce"] = [HumanMessage(role="system", content=json.dumps(customers, cls=CustomJSONEncoder))]
            #logger.debug("Successfully fetched customers.")
            return {"get_customers_responce": state["get_customers_responce"]}
    except Exception as e:
        logger.error(f"Error fetching customers: {e}")
        return {"get_customers_responce": [HumanMessage(role="system", content=json.dumps({"error": str(e)}, cls=CustomJSONEncoder))]}

def get_orders(state: AgentGraphState):
    try:
        #logger.debug("Fetching orders from the database.")
        with engine.connect() as connection:
            result = connection.execute(select(orders_table))
            orders = [serialize_record(row) for row in result]
            state["get_orders_responce"] = [HumanMessage(role="system", content=json.dumps(orders, cls=CustomJSONEncoder))]
            #logger.debug("Successfully fetched orders.")
            return {"get_orders_responce": state["get_orders_responce"]}
    except Exception as e:
        logger.error(f"Error fetching orders: {e}")
        return {"get_orders_responce": [HumanMessage(role="system", content=json.dumps({"error": str(e)}, cls=CustomJSONEncoder))]}

def get_faq(state: AgentGraphState):
    try:
        #logger.debug("Fetching FAQs from the database.")
        with engine.connect() as connection:
            result = connection.execute(select(faq_table))
            faqs = [serialize_record(row) for row in result]
            state["get_faq_responce"] = [HumanMessage(role="system", content=json.dumps(faqs, cls=CustomJSONEncoder))]
            #logger.debug("Successfully fetched FAQs.")
            return {"get_faq_responce": state["get_faq_responce"]}
    except Exception as e:
        logger.error(f"Error fetching FAQs: {e}")
        return {"get_faq_responce": [HumanMessage(role="system", content=json.dumps({"error": str(e)}, cls=CustomJSONEncoder))]}

# Create tools
tools = [
    # Tool.from_function(
    #     func=edesk_tool,
    #     name="edesk_tool",
    #     description="Creates a helpdesk ticket using information extracted from the AgentGraphState.",
    # ),
    
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
