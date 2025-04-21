from django.db import models
from django.contrib.auth.models import User

class Sale(models.Model):
    SALE_STATUS_CHOICES = [
        ('Active Ask', 'Active Ask'),
        ('Pending', 'Pending'),
        ('Shipping', 'Shipping'),
        ('Processing', 'Processing'),
        ('Completed', 'Completed'),
        ('Canceled', 'Canceled'),
    ]
    
    class Meta:
        ordering = ['-date']

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sales')
    # แก้ไขตรงนี้จาก 'product.Product' เป็น 'shop.Product'
    product = models.ForeignKey('shop.Product', on_delete=models.CASCADE, related_name='sales')
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=SALE_STATUS_CHOICES, default='Active Ask')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"Sale {self.id} - {self.product.collection.name} (Price: {self.price})"


class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('Place Bid', 'Place Bid'),
        ('Pending', 'Pending'),
        ('Shipping', 'Shipping'),
        ('Processing', 'Processing'),
        ('Completed', 'Completed'),
        ('Canceled', 'Canceled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    # แก้ไขตรงนี้จาก 'product.Product' เป็น 'shop.Product'
    product = models.ForeignKey('shop.Product', on_delete=models.CASCADE, related_name='orders')
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='Pending')
    # แก้ไขตรงนี้จาก 'user.Address' เป็น 'shop.Address'
    shipping_address = models.ForeignKey('shop.Address', on_delete=models.PROTECT, related_name='orders')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"Order {self.id} - {self.product.collection.name}"


class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('credit_debit_card', 'Credit Card/Debit Card'),
        ('paypal', 'PayPal'),
        ('bank_transfer', 'Bank Transfer'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('canceled', 'Canceled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Payment {self.id} - Order {self.order.id} - {self.amount}'