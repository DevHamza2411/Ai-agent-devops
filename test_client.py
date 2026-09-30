import requests

# The URL where your FastAPI app is running
API_URL = "http://localhost:8000/v1/chat"

# The data payload matching your AgentQuery schema
payload = {
    "question": "Can you check the log counts for the file /var/log/nginx/error.log?"
}

print("Sending request to DevOps Agent API...")
response = requests.post(API_URL, json=payload)

if response.status_code == 200:
    result = response.json()
    print("\n--- Agent Response ---")
    print(result["answer"])
else:
    print(f"Error {response.status_code}: {response.text}")
