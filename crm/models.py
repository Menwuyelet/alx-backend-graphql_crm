from django.db import models
from django.core.validators import MinValueValidator, RegexValidator
from django.utils import timezone

phone_validator = RegexValidator(
    regex=r'^(\+\d{1,3}\d{4,14}|(\d{3}-\d{3}-\d{4}))$',
    message="Phone number must be in +1234567890 or 123-456-7890 format."
)

class Customer(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True, validators=[phone_validator])

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    order_date = models.DateTimeField(default=timezone.now)