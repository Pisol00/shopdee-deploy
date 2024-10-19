from django.contrib import admin
from .models import Category, Brand, Collection, Product, CollectionImage
from .forms import CategoryForm, BrandForm, CollectionForm, ProductForm, CollectionImageForm

class CategoryAdmin(admin.ModelAdmin):
    form = CategoryForm
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name', 'description']

class BrandAdmin(admin.ModelAdmin):
    form = BrandForm
    list_display = ['name', 'description', 'img_url']
    search_fields = ['name']

class CollectionAdmin(admin.ModelAdmin):
    form = CollectionForm
    list_display = ['name', 'category', 'brand', 'colorway', 'created_at']
    search_fields = ['name', 'category__name', 'brand__name']
    list_filter = ['category', 'brand']

class ProductAdmin(admin.ModelAdmin):
    form = ProductForm
    list_display = ['collection', 'size_clothing', 'size_shoes', 'price', 'quantity', 'condition', 'created_at']
    search_fields = ['collection__name', 'seller__username']
    list_filter = ['condition', 'collection']

class CollectionImageAdmin(admin.ModelAdmin):
    form = CollectionImageForm
    list_display = ['collection', 'image_url', 'is_primary']
    search_fields = ['collection__name']
    list_filter = ['collection', 'is_primary']


admin.site.register(Category, CategoryAdmin)
admin.site.register(Brand, BrandAdmin)
admin.site.register(Collection, CollectionAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(CollectionImage, CollectionImageAdmin)
