from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from django.db.models import Count
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from shop.models import Collection, Product, ProductReview, UsedProductImage, Address
from shop.forms import ProductReviewForm
from shop.utils import get_reviews_for_collection, get_random_collections
from shop.mixins import ShopLoginRequiredMixin

class ProductSelectSizeView(ShopLoginRequiredMixin, View):
    def get_size_options(self, category_name, collection):
        """Returns sorted size options based on the product category and availability, excluding products with orders."""
        if category_name == "Apparel":
            size_options = Product.objects.filter(
                collection=collection
            ).annotate(
                num_orders=Count('orders')
            ).filter(
                num_orders=0
            ).values_list(
                'size_clothing', flat=True
            ).distinct().exclude(size_clothing=None)

            size_order = ["XXS", "XS", "S", "M", "L", "XL", "XXL", "3XL", "4XL", "FREE SIZE"]
        
        elif category_name == "Shoes":
            size_options = Product.objects.filter(
                collection=collection
            ).annotate(
                num_orders=Count('orders')
            ).filter(
                num_orders=0
            ).values_list(
                'size_shoes', flat=True
            ).distinct().exclude(size_shoes=None)

            size_order = ["US4", "US4.5", "US5", "US5.5", "US6", "US6.5", "US7", "US7.5", "US8", "US8.5", 
                          "US9", "US9.5", "US10", "US10.5", "US11", "US11.5", "US12", "US12.5", 
                          "US13", "US13.5", "US14", "US14.5", "US15", "US15.5", "US16", 
                          "US16.5", "US17", "US17.5", "US18"]
        else:
            size_options = []
            size_order = []

        return sorted(size_options, key=lambda size: size_order.index(size) if size in size_order else len(size_order))

    def get(self, request, collection_id):
        collection = Collection.objects.get(pk=collection_id)
        category_name = collection.category.name
        action = request.GET.get('action', 'buy')

        # Fetch and sort size options
        sorted_size_options = self.get_size_options(category_name, collection)

        # Fetch only available products that have no orders
        available_products = Product.objects.filter(
            collection=collection
        ).annotate(
            num_orders=Count('orders')
        ).filter(
            num_orders=0
        )

        # Check if there are brand new or used products available
        has_brand_new = available_products.filter(condition='brand_new').exists()
        has_used = available_products.filter(condition='used').exists()

        # Fetch reviews and random collections
        reviews_with_ratings = get_reviews_for_collection(collection)
        random_collections = get_random_collections(collection)

        context = {
            'collection': collection,
            'images': collection.images.all(),
            'size_options': sorted_size_options,
            'category': collection.category,
            'action': action,
            'has_brand_new': has_brand_new,
            'has_used': has_used,
            'reviews_with_ratings': reviews_with_ratings,
            'random_collections': random_collections,
        }

        return render(request, "./products/product_size.html", context)


class ShowProductByConditionView(ShopLoginRequiredMixin, View):
    def get(self, request):
        collection_id = request.GET.get('collection_id')
        size = request.GET.get('size')
        category = request.GET.get('category')  # ดึง category จาก URL
        condition_select = request.GET.get('condition')  # ดึง condition จาก URL

        # ดึง Collection หรือส่งกลับ 404 ถ้าไม่พบ
        collection = get_object_or_404(Collection, pk=collection_id)

        # กำหนด queryset ของผลิตภัณฑ์
        product_queryset = self.get_products(collection, category, condition_select, size)

        # เพิ่ม primary_image ให้กับสินค้าทั้งหมดใน product_queryset
        for product in product_queryset:
            product.image_url = self.get_first_image_url(product)

        addresses = Address.objects.filter(user=request.user)  # เปลี่ยนเป็นผู้ใช้ปัจจุบัน
        reviews_with_ratings = get_reviews_for_collection(collection)
        random_collections = get_random_collections(collection)

        context = {
            'collection': collection,
            'products': product_queryset,  # ส่งรายการสินค้าที่ดึงมา
            'size': size,
            'addresses': addresses,
            'images': collection.images.all(),
            'reviews_with_ratings': reviews_with_ratings,
            'random_collections': random_collections
        }

        return render(request, "./products/buy/show-by-condition.html", context)

    def get_products(self, collection, category, condition_select, size):
        """ดึงสินค้าตามเงื่อนไขที่กำหนด"""
        if category == 'Shoes':
            return collection.product_set.filter(
                condition=condition_select,
                size_shoes=size
            ).annotate(num_orders=Count('orders')).filter(num_orders=0)
        elif category == 'Clothing':
            return collection.product_set.filter(
                condition=condition_select,
                size_clothing=size
            ).annotate(num_orders=Count('orders')).filter(num_orders=0)
        else:
            return collection.product_set.filter(
                condition=condition_select
            ).annotate(num_orders=Count('orders')).filter(num_orders=0)

    def get_first_image_url(self, product):
        """ดึง URL ของรูปภาพแรกของสินค้า"""
        product_image = UsedProductImage.objects.filter(product=product).first()
        return product_image.image.url if product_image else None


class ProductReviewView(ShopLoginRequiredMixin, View):
    def get(self, request, product_id):
        product = get_object_or_404(Product, pk=product_id)
        form = ProductReviewForm()
        reviews = product.productreview_set.all()  # ดึงรีวิวทั้งหมดสำหรับผลิตภัณฑ์นี้
        return render(request, 'profiles/buying/product-review.html', {
            'form': form, 
            'product': product, 
            'reviews': reviews
        })

    def post(self, request, product_id):
        product = get_object_or_404(Product, pk=product_id)
        form = ProductReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user  # ตั้งค่าผู้ใช้ที่รีวิว
            review.save()
            messages.success(request, "Your review has been submitted.")
            return redirect('profile')
            
        reviews = product.productreview_set.all()
        return render(request, 'profiles/buying/product-review.html', {
            'form': form, 
            'product': product, 
            'reviews': reviews
        })