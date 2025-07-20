import requests

API_TOKEN = "your_token_here"
BASE_URL = "https://api.edesk.com/v2/channels"
HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

response = requests.get(BASE_URL, headers=HEADERS)

if response.status_code == 200:
    channels = response.json().get("channels", [])
    for ch in channels:
        print(f"ID: {ch.get('id')} | Name: {ch.get('name')} | Type: {ch.get('type')} | Email: {ch.get('email')}")
else:
    print("❌ Failed to retrieve channels:", response.status_code, response.text)
