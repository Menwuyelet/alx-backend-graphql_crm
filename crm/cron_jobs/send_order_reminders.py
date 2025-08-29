#!/usr/bin/env python3
import sys
import logging
from datetime import datetime, timedelta
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

LOG_FILE = "/tmp/order_reminders_log.txt"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def main():
    transport = RequestsHTTPTransport(
        url="http://localhost:8000/graphql",
        verify=True,
        retries=3,
    )
    client = Client(transport=transport, fetch_schema_from_transport=True)

    today = datetime.utcnow()
    week_ago = today - timedelta(days=7)

    query = gql(
        """
        query GetRecentOrders($start: DateTime!, $end: DateTime!) {
          orders(filter: {orderDate_Gte: $start, orderDate_Lte: $end, status: "PENDING"}) {
            id
            customer {
              email
            }
          }
        }
        """
    )

    try:
        result = client.execute(query, variable_values={
            "start": week_ago.isoformat(),
            "end": today.isoformat()
        })

        orders = result.get("orders", [])
        for order in orders:
            order_id = order["id"]
            customer_email = order["customer"]["email"]
            logging.info(f"Reminder: Order ID {order_id}, Customer Email {customer_email}")

        print("Order reminders processed!")

    except Exception as e:
        logging.error(f"Error fetching orders: {e}")
        print("Failed to process order reminders!", file=sys.stderr)


if __name__ == "__main__":
    main()
