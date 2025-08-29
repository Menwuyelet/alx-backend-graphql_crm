import graphene
from graphene_django import DjangoObjectType
from django.db import transaction
from django.utils import timezone
from django.core.validators import validate_email, RegexValidator
from django.core.exceptions import ValidationError
from .models import Customer, Order
from crm.models import Product

class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone")

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "price", "stock")

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = ("id", "customer", "products", "total_amount", "order_date")

class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()

class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Float(required=True)
    stock = graphene.Int()

class OrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.DateTime()


class CreateCustomer(graphene.Mutation):
    customer = graphene.Field(CustomerType)
    success = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        input = CustomerInput(required=True)

    def mutate(self, info, input):
        # Validate email
        try:
            validate_email(input.email)
        except ValidationError:
            return CreateCustomer(success=False, message="Invalid email format", customer=None)

        # Check uniqueness
        if Customer.objects.filter(email=input.email).exists():
            return CreateCustomer(success=False, message="Email already exists", customer=None)

        # Validate phone
        if input.phone:
            phone_validator = RegexValidator(
                regex=r'^(\+\d{1,3}\d{4,14}|(\d{3}-\d{3}-\d{4}))$',
                message="Phone must be in +1234567890 or 123-456-7890 format"
            )
            try:
                phone_validator(input.phone)
            except ValidationError:
                return CreateCustomer(success=False, message="Invalid phone format", customer=None)

        customer = Customer.objects.create(
            name=input.name, email=input.email, phone=input.phone
        )
        return CreateCustomer(success=True, message="Customer created successfully", customer=customer)


class BulkCreateCustomers(graphene.Mutation):
    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    def mutate(self, info, input):
        created_customers = []
        errors = []

        with transaction.atomic():
            for idx, cust_input in enumerate(input):
                result = CreateCustomer.mutate(CreateCustomer, info, input=cust_input)
                if result.customer:
                    created_customers.append(result.customer)
                else:
                    errors.append(f"Index {idx}: {result.message}")

        return BulkCreateCustomers(customers=created_customers, errors=errors)


class CreateProduct(graphene.Mutation):
    product = graphene.Field(ProductType)
    success = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        input = ProductInput(required=True)

    def mutate(self, info, input):
        stock = input.stock or 0
        if input.price <= 0:
            return CreateProduct(success=False, message="Price must be positive", product=None)
        if stock < 0:
            return CreateProduct(success=False, message="Stock cannot be negative", product=None)

        product = Product.objects.create(name=input.name, price=input.price, stock=stock)
        return CreateProduct(success=True, message="Product created successfully", product=product)


class CreateOrder(graphene.Mutation):
    order = graphene.Field(OrderType)
    success = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        input = OrderInput(required=True)

    def mutate(self, info, input):
        # Validate customer
        try:
            customer = Customer.objects.get(pk=input.customer_id)
        except Customer.DoesNotExist:
            return CreateOrder(success=False, message="Invalid customer ID", order=None)

        # Validate products
        products = Product.objects.filter(pk__in=input.product_ids)
        if not products.exists():
            return CreateOrder(success=False, message="No valid products found", order=None)
        if len(input.product_ids) != products.count():
            return CreateOrder(success=False, message="Some product IDs are invalid", order=None)

        total_amount = sum(p.price for p in products)
        order = Order.objects.create(
            customer=customer,
            total_amount=total_amount,
            order_date=input.order_date or timezone.now()
        )
        order.products.set(products)
        return CreateOrder(success=True, message="Order created successfully", order=order)



class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()



class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hello, GraphQL!")
    customers = graphene.List(CustomerType)
    products = graphene.List(ProductType)
    orders = graphene.List(OrderType)

    def resolve_customers(root, info):
        return Customer.objects.all()

    def resolve_products(root, info):
        return Product.objects.all()

    def resolve_orders(root, info):
        return Order.objects.all()


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "stock")


class UpdateLowStockProducts(graphene.Mutation):
    class Arguments:
        increment = graphene.Int(required=False, default_value=10)

    success = graphene.Boolean()
    message = graphene.String()
    updated_products = graphene.List(ProductType)

    def mutate(self, info, increment=10):
        low_stock_products = Product.objects.filter(stock__lt=10)

        updated = []
        for product in low_stock_products:
            product.stock += increment
            product.save()
            updated.append(product)

        message = (
            f"{len(updated)} products restocked by {increment} units"
            if updated else "No products needed restocking"
        )

        return UpdateLowStockProducts(
            success=True,
            message=message,
            updated_products=updated
        )


class Mutation(graphene.ObjectType):
    update_low_stock_products = UpdateLowStockProducts.Field()


schema = graphene.Schema(mutation=Mutation)