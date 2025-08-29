import logging
from datetime import datetime
import requests

LOG_FILE = "/tmp/crm_heartbeat_log.txt"

def log_crm_heartbeat():
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")

    message = f"{timestamp} CRM is alive"

    try:
        response = requests.post(
            "http://localhost:8000/graphql",
            json={"query": "{ hello }"},
            timeout=5
        )
        if response.ok and "data" in response.json():
            hello_value = response.json()["data"].get("hello", "No response")
            message += f" | GraphQL says: {hello_value}"
        else:
            message += " | GraphQL check failed"
    except Exception as e:
        message += f" | GraphQL error: {e}"


    with open(LOG_FILE, "a") as f:
        f.write(message + "\n")

    logging.basicConfig(filename=LOG_FILE, level=logging.INFO)
    logging.info(message)
