#!/bin/bash


cd "$(dirname "$0")/../.."

DELETED_COUNT=$(python3 manage.py shell -c "
from django.utils import timezone
from datetime import timedelta
from crm.models import Customer

one_year_ago = timezone.now() - timedelta(days=365)
inactive_customers = Customer.objects.filter(
    orders__isnull=True, created_at__lt=one_year_ago
) | Customer.objects.exclude(orders__created_at__gte=one_year_ago)

count = inactive_customers.count()
inactive_customers.delete()
print(count)
")

echo \"\$(date '+%Y-%m-%d %H:%M:%S') - Deleted \$DELETED_COUNT inactive customers\" >> /tmp/customer_cleanup_log.txt