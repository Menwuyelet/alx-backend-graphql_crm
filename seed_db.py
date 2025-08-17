import os
import django
from decimal import Decimal

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "alx_backend_graphql.settings")
django.setup()

from crm.models import Customer, Product, Order


def reset_tables():
    """Delete all existing records to start fresh."""
    print("🗑️ Clearing old data...")
    Order.objects.all().delete()
    Product.objects.all().delete()
    Customer.objects.all().delete()


def create_customers():
    """Seed the database with sample customers."""
    print("👤 Adding customers...")
    customer_entries = [
        {"name": "Alice Johnson", "email": "alice@example.com", "phone": "+1234567890"},
        {"name": "Bob Smith", "email": "bob@example.com", "phone": "123-456-7890"},
        {"name": "Carol Davis", "email": "carol@example.com", "phone": "+1987654321"},
        {"name": "David Wilson", "email": "david@example.com"},
        {"name": "Eva Brown", "email": "eva@example.com", "phone": "987-654-3210"},
    ]

    customers = [Customer.objects.create(**entry) for entry in customer_entries]
    for c in customers:
        print(f"   ✅ {c.name} ({c.email})")
    return customers


def create_products():
    """Seed the database with sample products."""
    print("📦 Adding products...")
    product_entries = [
        {"name": "Laptop", "price": Decimal("999.99"), "stock": 50},
        {"name": "Wireless Mouse", "price": Decimal("29.99"), "stock": 100},
        {"name": "Mechanical Keyboard", "price": Decimal("79.99"), "stock": 75},
        {"name": "4K Monitor", "price": Decimal("299.99"), "stock": 30},
        {"name": "Noise-Cancelling Headphones", "price": Decimal("149.99"), "stock": 60},
    ]

    products = [Product.objects.create(**entry) for entry in product_entries]
    for p in products:
        print(f"   ✅ {p.name} - ${p.price}")
    return products


def create_orders(customers, products):
    """Generate sample orders for customers."""
    print("🛒 Creating orders...")
    order_entries = [
        (customers[0], [products[0], products[1]]),  # Laptop + Mouse
        (customers[1], [products[2], products[3]]),  # Keyboard + Monitor
        (customers[2], [products[4]]),               # Headphones
        (customers[3], [products[0], products[2], products[4]]),  # Laptop + Keyboard + Headphones
        (customers[4], [products[1], products[3]]),  # Mouse + Monitor
    ]

    for idx, (cust, items) in enumerate(order_entries, start=1):
        total_price = sum(item.price for item in items)
        order = Order.objects.create(customer=cust, total_amount=total_price)
        order.products.set(items)
        item_names = ", ".join(p.name for p in items)
        print(f"   ✅ Order #{order.id}: {cust.name} → {item_names} (${order.total_amount})")


def run_seeder():
    """Main seeding workflow."""
    print("\n🌱 Seeding database...\n")
    reset_tables()
    customers = create_customers()
    products = create_products()
    create_orders(customers, products)

    print("\n🎉 Seeding complete!")
    print("📊 Stats:")
    print(f"   - Customers: {Customer.objects.count()}")
    print(f"   - Products: {Product.objects.count()}")
    print(f"   - Orders: {Order.objects.count()}")


if __name__ == "__main__":
    run_seeder()
