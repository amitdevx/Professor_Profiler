import logging
logging.basicConfig(level=logging.DEBUG)
from google.adk.clients.nim_client import NIMClient
client = NIMClient()
print("Client:", client.client)
print("API Key:", client.api_key)
