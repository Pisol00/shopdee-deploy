from django.db import models
from django.contrib.auth.models import User

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
    colorway = models.CharField(max_length=255, blank=True, null=True)
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

    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    size_clothing = models.CharField(max_length=50, choices=SIZE_CHOICES_CLOTHING, blank=True, null=True)
    size_shoes = models.CharField(max_length=50, choices=SIZE_CHOICES_SHOES, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=1)
    quantity = models.PositiveIntegerField(default=0)
    has_defect = models.BooleanField(default=False, blank=True, null=True)
    equipment = models.CharField(max_length=255, blank=True, null=True)
    condition = models.CharField(max_length=10, choices=CONDITION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Product in {self.collection.name} - Size: {self.get_size_display()}, Condition: {self.get_condition_display()}'
    
    def get_size_display(self):
        """แสดงขนาดของสินค้า"""
        if self.size_clothing:
            return self.size_clothing
        elif self.size_shoes:
            return self.size_shoes
        return "One Size"


class CollectionImage(models.Model):
    collection = models.ForeignKey(Collection, related_name='images', on_delete=models.CASCADE)
    image_url = models.URLField()
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return f'Image for Collection: {self.collection.name}'


class UsedProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE) 
    image = models.ImageField(upload_to='uploads/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'User-uploaded Image for {self.product.collection.name}'


class ProductReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
    review_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Review for {self.product.collection.name} by {self.user.username}'