import requests

client_id = "3f210ca6-ea38-4e6a-b883-9598bbea08bd"
client_secret = "0bNoacm40mKs99lpJc7VkfzUiv8wj0NGLJefW0th"

# Step 1: Get access token
response = requests.post("https://api.prokerala.com/token", data={
    "grant_type": "client_credentials",
    "client_id": client_id,
    "client_secret": client_secret
})
print("🔐 Token Response:", response.status_code, response.text)
