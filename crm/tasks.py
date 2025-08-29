from celery import shared_task
from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

LOG_FILE = "/tmp/crm_report_log.txt"

@shared_task
def generate_crm_report():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            verify=True,
            retries=3,
        )
        client = Client(transport=transport, fetch_schema_from_transport=True)

        query = gql(
            """
            query {
              totalCustomers
              totalOrders
              totalRevenue
            }
            """
        )
        result = client.execute(query)

        customers = result.get("totalCustomers", 0)
        orders = result.get("totalOrders", 0)
        revenue = result.get("totalRevenue", 0)

        log_message = f"{timestamp} - Report: {customers} customers, {orders} orders, {revenue} revenue"

    except Exception as e:
        log_message = f"{timestamp} - Error generating report: {e}"

    with open(LOG_FILE, "a") as f:
        f.write(log_message + "\n")

    return log_message
