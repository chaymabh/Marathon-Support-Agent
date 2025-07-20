from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv("/mnt/h100-volume/Gen_Search_Agent/.env")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def get_open_ai(temperature=0.1, model='gpt-4o'):
    llm = ChatOpenAI(
        model=model,
        temperature=temperature,
        openai_api_key=OPENAI_API_KEY,
    )
    return llm

def get_open_ai_json(temperature=0, model='gpt-4o'):
    llm = ChatOpenAI(
        model=model,
        temperature=temperature,
        openai_api_key=OPENAI_API_KEY,
        model_kwargs={"response_format": {"type": "json_object"}},
    )
    return llm
