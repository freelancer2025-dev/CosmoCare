import uuid
from django.db import models
from django.contrib.auth.models import User
from accounts.models import Address
from catalog.models import Product

class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending payment"
        PLACED = "PLACED", "Placed"
        PROCESSING = "PROCESSING", "Processing"
        SHIPPED = "SHIPPED", "Shipped"
        DELIVERED = "DELIVERED", "Delivered"
        CANCEL_REQUESTED = "CANCEL_REQUESTED", "Cancellation requested"
        CANCELLED = "CANCELLED", "Cancelled"
    class PaymentStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PAID = "PAID", "Paid"
        FAILED = "FAILED", "Failed"
        REFUND_PENDING = "REFUND_PENDING", "Refund pending"
        REFUNDED = "REFUNDED", "Refunded"
    order_number = models.CharField(max_length=24, unique=True, editable=False)
    public_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="orders")
    full_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True)
    address_text = models.TextField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    shipping = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=[("RAZORPAY","Razorpay"),("COD","Cash on Delivery")])
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    status = models.CharField(max_length=24, choices=Status.choices, default=Status.PENDING)
    cancellation_reason = models.TextField(blank=True)
    refund_reference = models.CharField(max_length=120, blank=True)
    qr_image = models.ImageField(upload_to="order_qr/", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def save(self, *args, **kwargs):
        if not self.order_number:
            import secrets
            self.order_number = "CC" + secrets.token_hex(5).upper()
        super().save(*args, **kwargs)
    def __str__(self): return self.order_number

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    product_name = models.CharField(max_length=180)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    @property
    def line_total(self): return self.unit_price * self.quantity

class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="payment")
    gateway_order_id = models.CharField(max_length=120, blank=True)
    gateway_payment_id = models.CharField(max_length=120, blank=True)
    signature = models.CharField(max_length=255, blank=True)
    amount_paise = models.PositiveIntegerField(default=0)
    raw_status = models.CharField(max_length=80, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
