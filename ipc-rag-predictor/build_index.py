import requests

print("Building IPC Index... Please wait (this may take 5-10 minutes)")
response = requests.post("http://localhost:8000/build-index")

print("Status Code:", response.status_code)
print("Response:", response.json())