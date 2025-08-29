import logging
from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

LOG_FILE = "/tmp/crm_heartbeat_log.txt"

def log_crm_heartbeat():
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")

    message = f"{timestamp} CRM is alive"

    try:
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            verify=True,
            retries=3,
        )
        client = Client(transport=transport, fetch_schema_from_transport=True)

        query = gql("{ hello }")
        result = client.execute(query)
        hello_value = result.get("hello", "No response")
        message += f" | GraphQL says: {hello_value}"

    except Exception as e:
        message += f" | GraphQL error: {e}"

    with open(LOG_FILE, "a") as f:
        f.write(message + "\n")

    logging.basicConfig(filename=LOG_FILE, level=logging.INFO)
    logging.info(message)
