import requests
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("API_KEY")

url = 'http://127.0.0.1:8004/ask' 
question = "i want to know the events that will happen in Munich soon in the following months?"
payload = {
    "user_id": "john.doe@example.com",
    "question": question,
    
}

headers = {
    "X-API-KEY": API_KEY
}

response = requests.post(url, json=payload, headers=headers)

if response.status_code == 200:
    response_data = response.json()
    print("User query:", question)
    print("Response:", response_data['response'])
    print("Execution Time:", response_data['execution_time'])
else:
    print(f"Error: {response.status_code}")
    print(response.text)
