from django.db import models
from django.contrib.auth.models import User

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipient_name = models.CharField(max_length=255)  # ชื่อผู้รับ
    phone_number = models.CharField(max_length=20, blank=True, null=True)  # หมายเลขโทรศัพท์
    address_line1 = models.CharField(max_length=255)  # เลขที่บ้าน และชื่อถนน
    address_line2 = models.CharField(max_length=255, blank=True)  # ซอย หรือข้อมูลเพิ่มเติม
    subdistrict = models.CharField(max_length=100)  # แขวง/ตำบล
    district = models.CharField(max_length=100)  # เขต/อำเภอ
    province = models.CharField(max_length=100)  # จังหวัด
    postal_code = models.CharField(max_length=20)  # รหัสไปรษณีย์
    country = models.CharField(max_length=100, default="Thailand")  # ประเทศ

    def __str__(self):
        return f'{self.recipient_name}, {self.address_line1}, {self.address_line2}, {self.subdistrict}, {self.district}, {self.province}, {self.postal_code}, {self.country}'



class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    img_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name


class Collection(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='collections')
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    name = models.CharField(max_length=255) 
    colorway = models.CharField(max_length=255, blank=True, null=True)  # เพิ่มฟิลด์ colorway ที่นี่
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    SIZE_CHOICES_CLOTHING = [
        ('XXS', 'XX-Small'),
        ('XS', 'X-Small'),
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', 'Extra Large'),
        ('XXL', 'XX Large'),
        ('3XL', '3X Large'),
        ('4XL', '4X Large'),
    ]

    SIZE_CHOICES_SHOES = [
        ('US4', '4'),
        ('US4.5', '4.5'),
        ('US5', '5'),
        ('US5.5', '5.5'),
        ('US6', '6'),
        ('US6.5', '6.5'),
        ('US7', '7'),
        ('US7.5', '7.5'),
        ('US8', '8'),
        ('US8.5', '8.5'),
        ('US9', '9'),
        ('US9.5', '9.5'),
        ('US10', '10'),
        ('US10.5', '10.5'),
        ('US11', '11'),
        ('US11.5', '11.5'),
        ('US12', '12'),
        ('US12.5', '12.5'),
        ('US13', '13'),
        ('US13.5', '13.5'),
        ('US14', '14'),
        ('US14.5', '14.5'),
        ('US15', '15'),
        ('US15.5', '15.5'),
        ('US16', '16'),
        ('US16.5', '16.5'),
        ('US17', '17'),
        ('US17.5', '17.5'),
        ('US18', '18'),
    ]
    
    CONDITION_CHOICES = [
        ('brand_new', 'Brand New'),
        ('used', 'Used'),
    ]

    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)  # เชื่อมโยงกับ Collection
    size_clothing = models.CharField(max_length=50, choices=SIZE_CHOICES_CLOTHING, blank=True, null=True)  # ขนาดของเสื้อผ้า
    size_shoes = models.CharField(max_length=50, choices=SIZE_CHOICES_SHOES, blank=True, null=True)  # ขนาดของรองเท้า
    price = models.DecimalField(max_digits=10, decimal_places=1)  # ราคา
    quantity = models.PositiveIntegerField(default=0)  # จำนวนสต็อก (สำหรับสินค้ามือหนึ่ง)
    has_defect = models.BooleanField(default=False, blank=True, null=True)  # สินค้ามีข้อบกพร่องหรือไม่ (สำหรับสินค้ามือสอง)
    equipment = models.CharField(max_length=255, blank=True, null=True)  # อุปกรณ์เพิ่มเติม (สำหรับสินค้ามือสอง)
    condition = models.CharField(max_length=10, choices=CONDITION_CHOICES)  # สถานะของสินค้า (ใหม่หรือมือสอง)
    created_at = models.DateTimeField(auto_now_add=True)  # วันที่สร้าง

    def __str__(self):
        return f'Product in {self.collection.name} - Size Clothing: {self.size_clothing}, Size Shoes: {self.size_shoes}, Condition: {self.condition}'

class CollectionImage(models.Model):
    collection = models.ForeignKey(Collection, related_name='images', on_delete=models.CASCADE)
    image_url = models.URLField()# หรือใช้ ImageField ถ้าต้องการเก็บไฟล์ภาพ
    is_primary = models.BooleanField(default=False)  # เพื่อระบุภาพหลัก

    def __str__(self):
        return f'Image for Collection: {self.collection.name}'


class UsedProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE) 
    image = models.ImageField(upload_to='uploads/')
    created_at = models.DateTimeField(auto_now_add=True)  # วันเวลาที่สร้าง
    updated_at = models.DateTimeField(auto_now=True)  # วันเวลาที่อัปเดตล่าสุด

    def __str__(self):
        return f'User-uploaded Image for {self.product.collection.name}'


class ProductReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
    review_date = models.DateTimeField(auto_now_add=True)

    #class Meta:
        #unique_together = ('product', 'user')  # เพิ่มข้อกำหนดให้ผู้ใช้สามารถรีวิวสินค้าหนึ่งได้เพียงครั้งเดียว

    def __str__(self):
        return f'Review for {self.product.collection.name} by {self.user.username}'


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
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sales')
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=SALE_STATUS_CHOICES, default='Active Ask')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"Sale {self.id} - {self.product.collection.name} (Price: {self.price})"


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlists')
    collections = models.ManyToManyField(Collection, related_name='wishlists')  

    def __str__(self):
        return f'Wishlist for {self.user.username}'


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
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='orders')
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='Pending')
    shipping_address = models.ForeignKey(Address, on_delete=models.PROTECT, related_name='orders')
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

    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('canceled', 'Canceled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')  # ผู้ใช้ที่ทำการชำระเงิน
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')  # คำสั่งซื้อที่เกี่ยวข้อง
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES)  # วิธีการชำระเงิน
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # จำนวนเงินที่ชำระ
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')  # สถานะการชำระเงิน
    payment_date = models.DateTimeField(auto_now_add=True)  # วันที่ทำการชำระเงิน

    def __str__(self):
        return f'Payment {self.id} - Order {self.order.id} - {self.amount}'
    
    
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts')  # ผู้ใช้ที่เกี่ยวข้อง
    created_at = models.DateTimeField(auto_now_add=True)  # วันที่สร้างตะกร้า
    updated_at = models.DateTimeField(auto_now=True)  # วันที่อัปเดตล่าสุด

    def __str__(self):
        return f'Cart for {self.user.username}'

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')  # ตะกร้าสินค้าที่เชื่อมโยง
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # สินค้าที่เลือกในตะกร้า
    quantity = models.PositiveIntegerField(default=1)  # จำนวนของสินค้าที่เพิ่มในตะกร้า

    def __str__(self):
        return f'{self.product.collection.name} - Quantity: {self.quantity} in cart of {self.cart.user.username}'

# class Bid(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bids')  # ผู้ใช้ที่ทำการประมูล
#     product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='bids')  # สินค้าที่ประมูล
#     bid_amount = models.DecimalField(max_digits=10, decimal_places=2)  # จำนวนเงินที่บิด
#     bid_time = models.DateTimeField(auto_now_add=True)  # วันที่และเวลาที่บิด

#     def __str__(self):
#         return f"Bid by {self.user.username} for {self.product.collection.name} - Amount: {self.bid_amount}"