from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field, field_validator
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage
from typing import Union, Any, Dict, Optional
from logging.handlers import RotatingFileHandler
import logging
import time
import asyncio
import re
import pytz
import gc
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from utils.logger import logger
from graph.graph import create_graph, compile_workflow

load_dotenv()

API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY not found in .env file")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def verify_api_key(api_key: str = Depends(api_key_header)):
    if api_key != API_KEY:
        logger.error(f"Invalid API key provided: {api_key}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return api_key

openai_server = "openai"
openai_model = 'gpt-4o'

verbose = False

logger = logging.getLogger("myapp")
logger.setLevel(logging.DEBUG)

if not logger.handlers:
    file_handler = RotatingFileHandler("app.log", maxBytes=5*1024*1024, backupCount=5)
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

call_responce_logger = logging.getLogger("call_responce")
call_responce_logger.setLevel(logging.DEBUG)

if not call_responce_logger.handlers:
    call_responce_handler = RotatingFileHandler('call_responce.log', maxBytes=5*1024*1024, backupCount=5)
    call_responce_handler.setLevel(logging.DEBUG)
    call_responce_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    call_responce_handler.setFormatter(call_responce_formatter)
    call_responce_logger.addHandler(call_responce_handler)

def validate_timezone(value: Optional[str]) -> str:
    if value and value not in pytz.all_timezones:
        logger.error(f"Invalid timezone: {value}")
        raise ValueError(f"Invalid timezone: {value}")
    timezone = value or "UTC"
    return timezone

def get_latest_final_report(memory: MemorySaver, thread_id: str) -> Union[Dict[str, Any], str]:
    try:
        checkpoints = memory.list({"configurable": {"thread_id": thread_id}})
    except Exception as e:
        logger.error(f"Failed to retrieve checkpoints: {str(e)}")
        return {"error": f"Failed to retrieve checkpoints: {str(e)}"}

    if not checkpoints:
        logger.warning(f"No checkpoints found for thread_id: {thread_id}")
        return {"error": "No checkpoints found."}

    latest_checkpoint = max(checkpoints, key=lambda cp: cp.checkpoint.get('ts', 0)).checkpoint
    final_reports = latest_checkpoint.get('channel_values', {}).get('reporter_responce', [])
    answer = "Sorry it seems like I lost connection to our servers."
    for report in final_reports:
        if isinstance(report, HumanMessage):
            content = getattr(report, 'content', None)
            if content:
                answer = content
    return answer

async def initialize_workflow():
    logger.info("Initializing workflow...")
    try:
        memory = MemorySaver()
        graph = create_graph(
            server=openai_server,
            model=openai_model,
            memory=memory
        )
        workflow = compile_workflow(graph, memory)

        app.state.openai_workflow = workflow
        app.state.openai_memory = memory

        logger.info("OpenAI workflow initialized successfully.")
    except Exception as e:
        logger.error(f"Error during workflow initialization: {e}")
        raise

async def workflow_reinitializer():
    logger.info("Starting workflow reinitializer...")
    while True:
        await asyncio.sleep(450)
        try:
            logger.info("Reinitializing workflow...")
            await initialize_workflow()
            logger.info("Workflow reinitialized successfully.")
        except Exception as e:
            logger.error(f"Scheduled reinitialization failed: {e}")

async def execute_workflow(question, user_id, thread_id, verbose=False):
    workflow = getattr(app.state, 'openai_workflow', None)
    memory = getattr(app.state, 'openai_memory', None)

    if not workflow or not memory:
        logger.error("OpenAI workflow is not initialized.")
        await initialize_workflow()
        logger.info("OpenAI workflow initialized.")

    dict_inputs = {"question": question, "user_id": user_id}
    config = {"configurable": {"thread_id": thread_id}}

    response = []
    start_time = time.time()

    try:
        async for event in workflow.astream(dict_inputs, config):
            if verbose:
                response.append(event)
            else:
                response.append("\n")
        logger.info(f"Workflow executed successfully for user {user_id}.")
    except Exception as e:
        error_message = str(e)
        logger.error(f"Error during workflow execution for user {user_id}: {error_message}")
        final_report = "Sorry it seems like I lost connection to the server"
        await initialize_workflow()
    else:
        final_report = get_latest_final_report(memory, thread_id)

    end_time = time.time()
    execution_time = end_time - start_time

    logger.info(f"Execution completed for user {user_id} in {execution_time:.2f} seconds.")

    return final_report, execution_time

class QuestionRequest(BaseModel):
    user_id: str = Field(..., description="User ID as an email")
    question: str = Field(..., min_length=1, description="The question to be asked")

    @field_validator('user_id')
    def validate_email(cls, value):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
            logger.error(f"Invalid email format: {value}")
            raise ValueError('must be a valid email')
        return value

@app.on_event("startup")
async def startup_event():
    try:
        await initialize_workflow()
    except Exception as e:
        logger.error(f"Initial workflow initialization failed: {e}")

    asyncio.create_task(workflow_reinitializer())

@app.post("/ask", status_code=200)
async def ask_question(request: QuestionRequest, api_key: str = Depends(verify_api_key)):
    question = request.question
    user_id = request.user_id

    thread_id = int(hash(user_id) % 10**10)
    final_report, execution_time = await execute_workflow(question=question, user_id=user_id, thread_id=thread_id, verbose=False)

    logger.info(f"Question processed successfully for user {user_id}.")

    return {
        "response": final_report,
        "execution_time": execution_time
    }