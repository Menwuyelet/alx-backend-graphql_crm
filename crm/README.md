# CRM Celery + Celery Beat Setup

This project uses Celery with Celery Beat to generate a weekly CRM report that summarizes total orders, customers, and revenue, logging the results to `/tmp/crm_report_log.txt`.

---

## Installation

Add the following to `requirements.txt`:


Install dependencies:
```bash
pip install -r requirements.txt

sudo apt update
sudo apt install redis-server
sudo systemctl enable redis-server
sudo systemctl start redis-server

redis-cli ping

python manage.py migrate

celery -A crm worker -l info

celery -A crm beat -l info

cat /tmp/crm_report_log.txt

```
