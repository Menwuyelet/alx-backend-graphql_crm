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



LOG_FILE = "/tmp/low_stock_updates_log.txt"

def update_low_stock():
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")

    try:
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            verify=True,
            retries=3,
        )
        client = Client(transport=transport, fetch_schema_from_transport=True)

        mutation = gql(
            """
            mutation {
              updateLowStockProducts {
                success
                message
                updatedProducts {
                  id
                  name
                  stock
                }
              }
            }
            """
        )

        result = client.execute(mutation)
        data = result["updateLowStockProducts"]

        log_message = f"{timestamp} | {data['message']}"
        if data["updatedProducts"]:
            for product in data["updatedProducts"]:
                log_message += f"\n - {product['name']} new stock: {product['stock']}"

    except Exception as e:
        log_message = f"{timestamp} | Error updating low stock: {e}"

    with open(LOG_FILE, "a") as f:
        f.write(log_message + "\n")

    logging.basicConfig(filename=LOG_FILE, level=logging.INFO)
    logging.info(log_message)