from django.db import models
from django.contrib.auth.models import User

from django.db import models

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('plates', 'Plates'),
        ('bowls', 'Bowls'),
        ('cups', 'Cups'),
        ('cutlery', 'Cutlery'),
        ('trays', 'Trays'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=3)  # Price in TND
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='plates')
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class TeamMember(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    bio = models.TextField()
    photo = models.ImageField(upload_to='team/')

    def __str__(self):
        return self.name

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart for {self.user.username}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def total_price(self):
        return self.quantity * self.product.price

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Charged', 'Charged'),  # Payment confirmed
        ('Processing', 'Processing'),  # Order is being prepared
        ('Shipped', 'Shipped'),  # Order is out for delivery
        ('Delivered', 'Delivered'),  # Order has been delivered
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')  # Order status
    location = models.CharField(max_length=100, blank=True, null=True)  # Current location
    estimated_delivery_time = models.DateTimeField(blank=True, null=True)  # Estimated delivery time

    def __str__(self):
        return f"Order #{self.id}"

    def update_estimated_delivery_time(self):
        # Calculate delivery time based on status
        if self.status == 'Charged':
            self.estimated_delivery_time = timezone.now() + timezone.timedelta(days=2)  # Example: 2 days after charging
        elif self.status == 'Processing':
            self.estimated_delivery_time = timezone.now() + timezone.timedelta(days=1)  # Example: 1 day after processing
        elif self.status == 'Shipped':
            self.estimated_delivery_time = timezone.now() + timezone.timedelta(hours=12)  # Example: 12 hours after shipping
        self.save()