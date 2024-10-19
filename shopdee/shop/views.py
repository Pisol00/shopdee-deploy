import json
import os
import random
from django.conf import settings
from django.urls import reverse
from django.views import View
from django.shortcuts import get_object_or_404, render, redirect
from .models import *
from django.db.models import Q
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import update_session_auth_hash
from .forms import *
from django.db.models import Min
import boto3
from django.conf import settings
from django.db.models import Count
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError
from django.core.files.storage import FileSystemStorage



def get_reviews_for_collection(collection):
    """ฟังก์ชันดึงรีวิวของผลิตภัณฑ์ในคอลเล็กชันนี้"""
    reviews = ProductReview.objects.filter(product__collection=collection).order_by('-review_date')

    def get_star_rating(rating):
        full_stars = '★' * rating
        empty_stars = '☆' * (5 - rating)
        return full_stars + empty_stars

    ratings = [get_star_rating(review.rating) for review in reviews]
    return list(zip(reviews, ratings))


def get_random_collections(current_collection):
    """ฟังก์ชันดึงคอลเล็กชันแรนด้อม โดยไม่เอาคอลเล็กชันที่กำลังแสดงอยู่"""
    collections = list(Collection.objects.exclude(id=current_collection.id).prefetch_related('images'))
    
    # ถ้าไม่มีคอลเล็กชันอื่น คืนค่าลิสต์เปล่า
    if not collections:
        return []

    # สุ่มเลือกคอลเล็กชันสูงสุด 4 รายการ
    random_collections = random.sample(collections, min(4, len(collections)))

    # เพิ่มภาพหลักให้กับแต่ละคอลเล็กชัน
    for collection in random_collections:
        collection.primary_image = collection.images.filter(is_primary=True).first()

    return random_collections


def get_starting_price(collection):
    """ฟังก์ชันคำนวณราคาต่ำสุดของคอลเล็กชัน"""
    return Product.objects.filter(collection=collection).aggregate(Min('price'))['price__min']


def attach_collection_data(collections):
    """เพิ่มข้อมูลราคา หมวดหมู่ และภาพหลักให้กับคอลเลกชัน"""
    categories = Category.objects.all()
    category_map = {category.id: category.name for category in categories}
    
    for collection in collections:
        collection.starting_price = get_starting_price(collection)
        collection.primary_image = collection.images.filter(is_primary=True).first()
        collection.category_name = category_map.get(collection.category.id) if collection.category else 'Unknown'



class HomePageView(View):
    def get(self, request):
        brands = Brand.objects.all()
        
        # แสดงคอลเลคชั่นล่าสุด 3 อันพร้อมราคาต่ำสุด
        recent_collections = self.get_recent_collections_with_prices(3)
        
        # คำนวณจำนวนคำสั่งซื้อในแต่ละคอลเล็กชัน
        most_popular_collections = self.get_most_popular_collections(3)
        
        # เตรียมข้อมูลสำหรับ rendering
        context = {
            'brands': brands,
            'collections': recent_collections,
            'most_popular_collections': most_popular_collections,
        }
        return render(request, "homepage.html", context)

    def get_recent_collections_with_prices(self, limit):
        """ดึงคอลเล็กชันล่าสุดพร้อมราคาต่ำสุด"""
        collections = Collection.objects.all().order_by('-created_at')[:limit]
        attach_collection_data(collections)
        return collections

    def get_most_popular_collections(self, limit):
        """ดึงคอลเล็กชันที่ขายดีที่สุดและเพิ่มข้อมูลภาพหลัก"""
        collections = Collection.objects.annotate(num_orders=Count('product__orders')).order_by('-num_orders')[:limit]
        attach_collection_data(collections)
        return collections


class ExploreView(View):
    def get(self, request):
        categories = Category.objects.all()
        brands = Brand.objects.all()
        price_ranges = request.GET.getlist('price_ranges')
        selected_categories = request.GET.getlist('categories')
        selected_brands = request.GET.getlist('brands')

        # ค้นหา collections พร้อมกับราคาต่ำสุดของแต่ละ collection
        collections = Collection.objects.prefetch_related('product_set').annotate(
            min_price=Min('product__price')  # ดึงราคาต่ำสุดจาก Product
        )

        if price_ranges:
            price_filter = Q()
            for price_range in price_ranges:
                if '-' in price_range:
                    min_max = price_range.split('-')
                    min_price = float(min_max[0]) if min_max[0] else 0  # ถ้าไม่มีค่า min ให้เป็น 0
                    max_price = float(min_max[1]) if len(min_max) > 1 and min_max[1] else None  # ถ้าไม่มีค่า max ให้เป็น None

                    if max_price is not None:
                        price_filter |= Q(product__price__gte=min_price, product__price__lte=max_price)
                    else:
                        price_filter |= Q(product__price__gte=min_price)
                else:
                    min_price = float(price_range)
                    price_filter |= Q(product__price__gte=min_price)
            collections = collections.filter(price_filter)


        if selected_categories:
            collections = collections.filter(category__id__in=selected_categories)

        if selected_brands:
            collections = collections.filter(brand__id__in=selected_brands)

        category_map = {category.id: category.name for category in categories}

        for collection in collections:
            collection.primary_image = collection.images.filter(is_primary=True).first()
            collection.category_name = category_map.get(collection.category.id) if collection.category else 'Unknown'

        context = {
            'collections': collections,
            'categories': categories,
            'brands': brands,
            'selected_categories': selected_categories,
            'selected_brands': selected_brands,
            'price_ranges': price_ranges,
        }

        return render(request, "explore.html", context)




class CollectionDetailView(LoginRequiredMixin, View):
    login_url = "/login/"
    permission_required = 'shop.add_product'
    
    def get(self, request, collection_id):
        # ดึงคอลเล็กชันหรือคืนค่า 404 ถ้าไม่พบ
        collection = get_object_or_404(Collection, pk=collection_id)

        # หาค่าราคาต่ำสุดและราคาผลิตภัณฑ์ใหม่
        min_price = collection.product_set.aggregate(Min('price'))['price__min']
        new_product_price = collection.product_set.filter(condition='brand_new').aggregate(Min('price'))['price__min']
        
        # ดึงราคาขายล่าสุด
        last_sale = collection.product_set.filter(orders__isnull=False).order_by('-orders__date').first()
        last_sale_price_value = last_sale.price if last_sale else None
        
        # ดึงภาพที่เกี่ยวข้องกับคอลเล็กชัน
        images = CollectionImage.objects.filter(collection=collection)
        primary_image = images.filter(is_primary=True).first()
        
        # ดึงรีวิวสำหรับคอลเล็กชัน
        reviews_with_ratings = get_reviews_for_collection(collection)
        
        # ดึงคอลเล็กชันแบบสุ่มโดยไม่รวมคอลเล็กชันปัจจุบัน
        random_collections = get_random_collections(collection)
        
        # ตั้งราคาตั้งต้นสำหรับคอลเล็กชันแบบสุ่ม
        for random_collection in random_collections:
            random_collection.starting_price = get_starting_price(random_collection)

        # เตรียม context สำหรับการเรนเดอร์เทมเพลต
        context = {
            'collection': collection,
            'min_price': min_price,
            'new_product_price': new_product_price,
            'last_sale_price': last_sale_price_value,
            'images': images,
            'primary_image': primary_image,
            'reviews_with_ratings': reviews_with_ratings, 
            'random_collections': random_collections,
            'can_add_product': request.user.has_perm('shop.add_product')
        }
        
        return render(request, './collections/collection.html', context)


class ProfileView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request):
        user = request.user

        context = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
        }
        return render(request, "profiles/profile/profile.html", context)
    

class EditProfileView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request):
        user = request.user
        form = EditProfileForm(instance=user)
        return render(request, 'profiles/profile/editprofile.html', {'form': form})

    def post(self, request):
        user = request.user
        form = EditProfileForm(request.POST, instance=user)

        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')
        else:
            messages.error(request, "There was an error updating your profile.")
        
        return render(request, 'profiles/profile/editprofile.html', {'form': form})

    def validate_profile_data(self, form, request):
        """ฟังก์ชันตรวจสอบความถูกต้องของข้อมูลโปรไฟล์"""
        first_name = form.data.get('first_name')
        last_name = form.data.get('last_name')
        email = form.data.get('email')

        # ตรวจสอบว่าทุกฟิลด์ต้องไม่ว่างเปล่า
        if not first_name or not last_name or not email:
            messages.error(request, "All fields are required.")
            return False

        # ตรวจสอบรูปแบบอีเมล
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Invalid email format. Please provide a valid email address.")
            return False

        # ตรวจสอบความถูกต้องของฟอร์ม
        return form.is_valid()
    

class AddressView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request):
        user = request.user

        addresses = Address.objects.filter(user=user)

        context = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'addresses': addresses
        }
        return render(request, "profiles/addresses/address.html", context)


class NewAddressView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request):
        user = request.user

        province_file = os.path.join(settings.BASE_DIR, 'shop', 'data', 'thai_province.json')
        district_file = os.path.join(settings.BASE_DIR, 'shop', 'data', 'thai_district.json')
        subdistrict_file = os.path.join(settings.BASE_DIR, 'shop', 'data', 'thai_subdistrict.json')

        with open(province_file, encoding='utf-8') as f:
            provinces = json.load(f)
        with open(district_file, encoding='utf-8') as f:
            districts = json.load(f)
        with open(subdistrict_file, encoding='utf-8') as f:
            subdistricts = json.load(f)


        #เรียงลำดับตามตัวอักษร A-Z
        provinces = sorted(provinces, key=lambda x: x['name_en'])
        districts = sorted(districts, key=lambda x: x['name_en'])
        subdistricts = sorted(subdistricts, key=lambda x: x['name_en'])

        form = AddressForm()
        context = {
            'form': form,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'provinces': provinces,
            'districts': districts,
            'subdistricts': subdistricts,
        }
        return render(request, "profiles/addresses/newaddress.html", context)

    def post(self, request):
        user = request.user
        form = AddressForm(request.POST)

        if form.is_valid():
            address = form.save(commit=False)
            address.user = user
            
            address.province = request.POST.get('province_name')
            address.district = request.POST.get('district_name')
            address.subdistrict = request.POST.get('subdistrict_name')
            
            address.save()
            messages.success(request, "New address has been saved successfully!") 
            return redirect('address')
        
        return render(request, "profiles/addresses/newaddress.html", {'form': form})

class EditAddressView(LoginRequiredMixin, View):
    login_url = "/login/"

    def load_location_data(self):
        """Load location data from JSON files."""
        province_file = os.path.join(settings.BASE_DIR, 'shop', 'data', 'thai_province.json')
        district_file = os.path.join(settings.BASE_DIR, 'shop', 'data', 'thai_district.json')
        subdistrict_file = os.path.join(settings.BASE_DIR, 'shop', 'data', 'thai_subdistrict.json')

        with open(province_file, encoding='utf-8') as f:
            provinces = json.load(f)
        with open(district_file, encoding='utf-8') as f:
            districts = json.load(f)
        with open(subdistrict_file, encoding='utf-8') as f:
            subdistricts = json.load(f)

        return provinces, districts, subdistricts

    def get(self, request, address_id):
        user = request.user
        try:
            address = Address.objects.get(pk=address_id, user=user)
        except Address.DoesNotExist:
            messages.error(request, "Address not found.")
            return redirect('address')  # Redirect to address list if not found

        provinces, districts, subdistricts = self.load_location_data()
        form = AddressForm(instance=address)

        context = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'form': form,
            'provinces': provinces,
            'districts': districts,
            'subdistricts': subdistricts
        }
        return render(request, "profiles/addresses/editaddress.html", context)

    def post(self, request, address_id):
        try:
            address = Address.objects.get(pk=address_id, user=request.user)
        except Address.DoesNotExist:
            messages.error(request, "Address not found.")
            return redirect('address')

        form = AddressForm(request.POST, instance=address)

        if form.is_valid():
            form.save()
            messages.success(request, "Address updated successfully!")
            return redirect('address')
        else:
            messages.error(request, "There were errors in your submission.")

        provinces, districts, subdistricts = self.load_location_data()

        context = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'form': form,
            'provinces': provinces,
            'districts': districts,
            'subdistricts': subdistricts
        }
        return render(request, "profiles/addresses/editaddress.html", context)

class DeleteAddressView(LoginRequiredMixin, View):
    login_url = "/login/"
    
    def post(self, request, address_id):
        address = get_object_or_404(Address, pk=address_id, user=request.user)
        
        try:
            with transaction.atomic():  # ใช้ transaction เพื่อให้มั่นใจในการดำเนินการ
                address.delete()
                messages.success(request, "Address deleted successfully.")
        except ProtectedError:
            messages.error(request, "Cannot delete this address because it is being used in an order.")
        except IntegrityError:
            messages.error(request, "An integrity error occurred while trying to delete the address.")
        
        return redirect('address')
       
class BuyingView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request):
        user = request.user
        status = request.GET.get('status', 'Place Bid')
        search_query = request.GET.get('search', '')

        orders = Order.objects.filter(user=user, status=status)

        if search_query:
            name_filter = Q(product__collection__name__icontains=search_query)

            try:
                order_id = int(search_query)
                id_filter = Q(id=order_id)
            except ValueError:
                id_filter = Q()

            orders = orders.filter(name_filter | id_filter)

        # คำนวณราคาจาก price * quantity
        for order in orders:
            order.price = order.price * order.quantity

        context = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'orders': orders,
            'current_status': status,
            'search_query': search_query
        }

        return render(request, "profiles/buying/buying.html", context)

class SellingView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request):
        user = request.user
        status = request.GET.get('status', 'Active Ask')
        search_query = request.GET.get('search', '')

        sales = Sale.objects.filter(user=user, status=status)

        if search_query:
            name_filter = Q(product__collection__name__icontains=search_query)

            try:
                sale_id = int(search_query)
                id_filter = Q(id=sale_id)
            except ValueError:
                id_filter = Q()

            sales = sales.filter(name_filter | id_filter)

        context = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'sales': sales,
            'current_status': status,
            'search_query': search_query
        }

        return render(request, "profiles/selling.html", context)

class ChangePasswordView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        form = ChangePasswordForm(user=request.user)  # ส่ง user ปัจจุบันเข้าไปในฟอร์ม
        return render(request, 'profiles/change_password.html', {'form': form})

    def post(self, request):
        form = ChangePasswordForm(user=request.user, data=request.POST)  # ส่ง user และข้อมูล POST เข้าไปในฟอร์ม
        if form.is_valid():
            user = request.user
            new_password = form.cleaned_data.get('new_password')

            # ตั้งค่ารหัสผ่านใหม่
            user.set_password(new_password)
            user.save()

            # อัปเดต session auth hash เพื่อให้ผู้ใช้ไม่ต้องล็อกอินใหม่
            update_session_auth_hash(request, user)

            messages.success(request, "Your password was successfully updated!")
            return redirect('change_password')
        else:
            messages.error(request, "There was an error updating your password.")
            return render(request, 'profiles/change_password.html', {'form': form})
    


class GetDistrictsView(LoginRequiredMixin, View):
    login_url = "/login/"
    
    def get(self, request, province_id):
        district_file = os.path.join(settings.BASE_DIR, 'shop', 'data', 'thai_district.json')

        with open(district_file, encoding='utf-8') as f:
            districts = json.load(f)

        filtered_districts = [d for d in districts if d['province_id'] == province_id]

        return JsonResponse({'districts': filtered_districts})

class GetSubdistrictsView(LoginRequiredMixin, View):
    login_url = "/login/"
    
    def get(self, request, district_id):
        subdistrict_file = os.path.join(settings.BASE_DIR, 'shop', 'data', 'thai_subdistrict.json')

        with open(subdistrict_file, encoding='utf-8') as f:
            subdistricts = json.load(f)

        filtered_subdistricts = [s for s in subdistricts if s['district_id'] == district_id]

        return JsonResponse({'subdistricts': filtered_subdistricts})


    


class ProductSelectSizeView(LoginRequiredMixin, View):
    login_url = "/login/"
    
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

        for random_collection in random_collections:
            random_collection.starting_price = get_starting_price(random_collection)

        # Build the context for the template
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




class ShowProductByConditionView(LoginRequiredMixin, View):
    login_url = "/login/"
    
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

        for random_collection in random_collections:
            random_collection.starting_price = get_starting_price(random_collection)

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
        if category == 'Shoes' or category == 'Clothing':
            return collection.product_set.filter(
                condition=condition_select,
                size_shoes=size
            ).annotate(num_orders=Count('orders')).filter(num_orders=0)  # ตรวจสอบจำนวนคำสั่งซื้อ
        else:
            return collection.product_set.filter(
                condition=condition_select
            ).annotate(num_orders=Count('orders')).filter(num_orders=0)

    def get_first_image_url(self, product):
        product_image = UsedProductImage.objects.filter(product=product).first()  # ดึงรูปภาพแรก
        return product_image.image.url if product_image else None  # ใช้ image.url เพื่อเข้าถึง URL ของภาพ


#หน้า checkout product แบบเดี่ยว และ หลายรายการ
class ProductCheckoutView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request):
        product_id = request.GET.get('product_id')
        condition = request.GET.get('condition')
        size = request.GET.get('size')
        collection_id = request.GET.get('collection_id')

        # ค้นหา Collection ตาม collection_id
        collection = Collection.objects.get(pk=collection_id)

        # ค้นหา Product ตาม product_id และ condition
        product = collection.product_set.get(id=product_id, condition=condition)

        # ค้นหา addresses ของผู้ใช้ปัจจุบัน
        addresses = Address.objects.filter(user=request.user)

        # ค้นหารูปภาพของสินค้า
        product_images = UsedProductImage.objects.filter(product=product)
        print(product_images)
        
        context = {
            'collection': collection,
            'product': product,
            'size': size,
            'addresses': addresses,
            'shipping_fee': 150,
            'collection_images': collection.images.all(),  # รูปภาพจาก Collection
            'product_images': product_images,  # รูปภาพจาก Product
        }

        return render(request, './products/buy/checkout.html', context)

    def post(self, request):
        product_id = request.POST.get('product_id')  # เปลี่ยนให้ดึงจาก POST แทน GET
        collection_id = request.POST.get('collection_id')
        shipping_address_id = request.POST.get('shipping_address')
        payment_method = request.POST.get('payment_method')

        # ค้นหา Product และ Collection
        product = Product.objects.get(id=product_id)
        collection = Collection.objects.get(pk=collection_id)

        if not shipping_address_id:
            messages.error(request, "Please select a shipping address.")
            return redirect(request.path)

        try:
            # เริ่ม transaction
            with transaction.atomic():
                # สร้าง Order
                order = Order.objects.create(
                    user=request.user,
                    product=product,
                    shipping_address_id=shipping_address_id,
                    price=product.price,
                    quantity=1  # ตั้งค่าเป็น 1 เนื่องจากไม่ให้เลือกจำนวน
                )

                # สร้าง Payment
                payment = Payment.objects.create(
                    user=request.user,
                    order=order,
                    payment_method=payment_method,
                    amount=product.price,
                    status='completed'
                )
                
            # เปลี่ยนไปยังหน้า Success หรือหน้าหลังจากชำระเงิน
            return redirect('payment_success', payment_id=payment.id)

        except Exception as e:
            messages.error(request, "There was an error processing your order: {}".format(str(e)))
            return redirect(request.path)

class CheckoutCartView(LoginRequiredMixin, View):
    login_url = "/login/"
    
    def get(self, request):
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            items = cart.items.all()
            total_price = sum(item.product.price * item.quantity for item in items)
        else:
            items = []
            total_price = 0

        addresses = Address.objects.filter(user=request.user)

        context = {
            'cart_items': items,
            'total_price': total_price,
            'addresses': addresses,
            'shipping_fee': 150,
        }
        return render(request, './products/buy/checkout_cart.html', context)

    def post(self, request):
        cart = Cart.objects.filter(user=request.user).first()
        shipping_fee = 150
        
        if not cart or not cart.items.exists():
            messages.error(request, "Your cart is empty.")
            return redirect(request.path)

        shipping_address_id = request.POST.get('address_id')
        payment_method = request.POST.get('payment_method')

        if not shipping_address_id:
            messages.error(request, "Please select a shipping address.")
            return redirect(request.path)

        if not payment_method:
            messages.error(request, "Please select a payment method.")
            return redirect(request.path)

        # สร้างคำสั่งซื้อและการชำระเงินสำหรับแต่ละรายการในตะกร้า
        try:
            with transaction.atomic():  # ใช้ transaction เพื่อป้องกันข้อผิดพลาด
                for item in cart.items.all():
                    # สร้างคำสั่งซื้อ
                    order = Order.objects.create(
                        user=request.user,
                        product=item.product,
                        shipping_address_id=shipping_address_id,
                        price=item.product.price,
                        quantity=item.quantity
                    )

                    # สร้างการชำระเงิน
                    payment = Payment.objects.create(
                        user=request.user,
                        order=order,
                        payment_method=payment_method,
                        amount=item.product.price * item.quantity + shipping_fee,
                        status='completed'
                    )

                # ล้างตะกร้าหลังจากทำการชำระเงินเรียบร้อย
                cart.items.all().delete()

            messages.success(request, "Payment successful!")
            return redirect('payment_success', payment_id=payment.id)

        except Exception as e:
            messages.error(request, f"An error occurred while processing your payment: {str(e)}")
            return redirect(request.path)
        

class PaymentSuccessView(LoginRequiredMixin,View):
    login_url = "/login/"
    def get(self, request, payment_id):
        payment = Payment.objects.get(id=payment_id)
        order = Order.objects.get(id=payment.order.id) 

        return render(request, './products/buy/payment_success.html', {
            'payment': payment,
            'order': order
        })
    
class SellDetailView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = "/login/"
    permission_required = 'shop.add_product'
    def get(self, request):
        collection_id = request.GET.get('collection_id')
        collection = Collection.objects.get(id=collection_id)
        
        # ดึง category ของ collection
        category = collection.category.name
        
        return render(request, './products/sell/sell_detail.html', {
            'collection': collection,
            'category': category,  # ส่ง category ไปยัง template
            'images': collection.images.all()
        })

    def post(self, request, *args, **kwargs):
        try:
            collection_id = request.GET.get('collection_id')
            size = request.POST.get('size')
            has_defect = request.POST.get('has_defect')
            equipment = request.POST.get('equipment')
            price = request.POST.get('price')
            images = request.FILES.getlist('images')  # ดึงข้อมูลไฟล์รูปภาพทั้งหมด
            print(request.FILES)
            print(images)
            
            # ตรวจสอบค่าที่ได้รับจากแบบฟอร์ม
            if not size or not price:
                return render(request, './products/sell/sell_detail.html', {
                    'error': 'Size and Price are required.',
                    'collection': collection  # หรือข้อมูลที่คุณต้องการแสดง
                })

            # เก็บข้อมูลลงใน session
            sell_data = {
                'collection_id': collection_id,
                'size': size,
                'has_defect': has_defect,
                'equipment': equipment,
                'price': price,
                'images': images  # เก็บไฟล์ภาพแทน
            }
            request.session['sell_data'] = sell_data

            # เปลี่ยนเส้นทางไปยังหน้าสรุป
            return redirect('sell_summary')

        except Exception as e:
            return render(request, './products/sell_detail.html', {
                'error': str(e),  # ส่งข้อผิดพลาดกลับไปยัง template
                'collection': collection  # หรือข้อมูลที่คุณต้องการแสดง
            })
            
class SellSummaryView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = "/login/"
    permission_required = 'shop.add_product'
    def get(self, request):
        # ดึงข้อมูลการขายจาก session
        sell_data = request.session.get('sell_data', {})
        
        if not sell_data:
            return redirect('sell-product')
        
        collection_id = sell_data.get('collection_id')
        collection = get_object_or_404(Collection, id=collection_id)
        
        price = float(sell_data.get('price', 0)) 
        transaction_fee = price * 0.07
        processing_fee = price * 0.03
        total_payout = price - (transaction_fee + processing_fee)
        
        context = {
            'collection': collection,
            'sell_data': sell_data,
            'transaction_fee': transaction_fee,
            'processing_fee': processing_fee,
            'total_payout': total_payout,
            'images': collection.images.all()
        }
        
        return render(request, './products/sell/sell_summary.html', context)
    
    def post(self, request):
        sell_data = request.session.get('sell_data', {})
        collection_id = sell_data.get('collection_id')
        size = request.POST.get('size')
        price = request.POST.get('price')
        has_defect = sell_data.get('has_defect') == 'True'
        equipment = request.POST.get('equipment')

        if not price:
            return self._render_summary_with_error(collection_id, sell_data, "ราคาจำเป็นต้องระบุ.")
        
        try:
            price = float(price)
        except ValueError:
            return self._render_summary_with_error(collection_id, sell_data, "รูปแบบราคาไม่ถูกต้อง.")

        collection = get_object_or_404(Collection, id=collection_id)
        size_clothing, size_shoes = self._get_sizes(collection, size)

        # รับภาพที่อัปโหลด
        uploaded_images = request.FILES.getlist('images')  # ดึงไฟล์ที่อัปโหลดทั้งหมด
        print(f'Uploaded images: {uploaded_images}')

        # เริ่มต้นการทำธุรกรรม
        try:
            with transaction.atomic():
                product = self._create_product(collection, size_clothing, size_shoes, price, has_defect, equipment)

                # บันทึกรูปภาพที่อัปโหลด
                for image in uploaded_images:
                    if not image.content_type.startswith('image/'):
                        return self._render_summary_with_error(collection_id, sell_data, "ไฟล์ที่อัปโหลดต้องเป็นภาพ.")
                    
                    UsedProductImage.objects.create(product=product, image=image)  # ใช้ฟิลด์ image

                # สร้าง instance ของ Sale
                Sale.objects.create(user=request.user, product=product, price=price)
                
                messages.success(request, "Successfully listed the product for sale!")
            
            return redirect('homepage')

        except Exception as e:
            print(f'Error occurred: {e}')
            return self._render_summary_with_error(collection_id, sell_data, "เกิดข้อผิดพลาดในการบันทึกข้อมูล: " + str(e))
    
    def _get_sizes(self, collection, size):
        """กำหนดขนาดตามประเภทของคอลเลกชัน."""
        if collection.category.name == 'Apparel':
            return size, None
        elif collection.category.name == 'Shoes':
            return None, size
        return None, None

    def _upload_images(self, images):
        """อัปโหลดภาพไปยัง Local Storage และส่งกลับ URL ของภาพ."""
        image_urls = []
        
        for image in images:
            # สร้างชื่อไฟล์ใหม่หรือใช้ชื่อเดิม
            file_path = f'uploads/{image.name}'  # กำหนดพาธที่ต้องการเก็บไฟล์
            
            # บันทึกไฟล์ลงใน Local Storage
            with open(os.path.join(settings.MEDIA_ROOT, file_path), 'wb+') as destination:
                for chunk in image.chunks():
                    destination.write(chunk)

            # เพิ่ม URL ของภาพที่จัดเก็บใน Local Storage ลงในลิสต์
            image_urls.append(f'{settings.MEDIA_URL}{file_path}')

        return image_urls

    def _create_product(self, collection, size_clothing, size_shoes, price, has_defect, equipment):
        """สร้าง instance ของ Product."""
        return Product.objects.create(
            collection=collection,
            size_clothing=size_clothing,
            size_shoes=size_shoes,
            price=price,
            has_defect=has_defect,
            equipment=equipment,
            condition='used' if has_defect else 'brand_new'
        )

    def _render_summary_with_error(self, collection_id, sell_data, error_message):
        """เรนเดอร์หน้าสรุปด้วยข้อความแสดงข้อผิดพลาด."""
        collection = get_object_or_404(Collection, id=collection_id)
        return render(
            request=self.request,
            template_name='./products/sell/sell_summary.html',
            context={
                'collection': collection,
                'error': error_message,
                'sell_data': sell_data
            }
        )


class WishListView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request):
        user = request.user
        wishlist, created = Wishlist.objects.get_or_create(user=user)
        
        # เพิ่มภาพหลักให้กับแต่ละคอลเล็กชัน
        collections_with_images = []
        for collection in wishlist.collections.all():
            primary_image = collection.images.filter(is_primary=True).first()
            collections_with_images.append({
                'collection': collection,
                'primary_image': primary_image
            })

        context = {
            'wishlist': collections_with_images
        }

        return render(request, "profiles/wishlist.html", context)

class RemoveFromWishlistView(LoginRequiredMixin, View):
    login_url = "/login/"
    
    def post(self, request, collection_id):
        wishlist = get_object_or_404(Wishlist, user=request.user)
        collection = get_object_or_404(Collection, id=collection_id)
        
        wishlist.collections.remove(collection)
        
        return redirect('wishlist')

class AddToWishlistView(LoginRequiredMixin, View):
    login_url = "/login/"
    
    def get(self, request, collection_id):
        collection = get_object_or_404(Collection, id=collection_id)
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)

        # ตรวจสอบว่าสินค้านั้นอยู่ใน Wishlist อยู่แล้วหรือไม่
        if collection in wishlist.collections.all():
            return JsonResponse({'status': 'already_added'})
        
        # ถ้ายังไม่มีใน Wishlist ให้เพิ่ม
        wishlist.collections.add(collection)
        return JsonResponse({'status': 'added'})

class ProductReviewView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request, product_id):
        product = get_object_or_404(Product, pk=product_id)
        form = ProductReviewForm()
        reviews = product.productreview_set.all()  # ดึงรีวิวทั้งหมดสำหรับผลิตภัณฑ์นี้
        return render(request, 'profiles/buying/product-review.html', {'form': form, 'product': product, 'reviews': reviews})

    def post(self, request, product_id):
        product = get_object_or_404(Product, pk=product_id)
        form = ProductReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user  # ตั้งค่าผู้ใช้ที่รีวิว
            review.save()
            messages.success(request, "Your review has been submitted.")
            return redirect('profile')  # เปลี่ยนเป็น URL ที่ต้องการ
        reviews = product.productreview_set.all()
        return render(request, 'profiles/buying/product-review.html', {'form': form, 'product': product, 'reviews': reviews})
    
class OrderDetailView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request, order_id):
        # ดึงคำสั่งซื้อที่ผู้ใช้ได้ทำการสั่งซื้อ
        order = get_object_or_404(Order, id=order_id, user=request.user)

        # ตรวจสอบการชำระเงินที่เกี่ยวข้อง
        payments = order.payments.all()  # ดึงการชำระเงินทั้งหมดที่เกี่ยวข้องกับคำสั่งซื้อ

        # ดึงที่อยู่การจัดส่ง
        shipping_address = order.shipping_address  # เข้าถึงที่อยู่การจัดส่ง

        # ตรวจสอบว่าสินค้าถูกรีวิวไปแล้ว
        product_reviews = ProductReview.objects.filter(product=order.product, user=request.user)
        is_reviewed = product_reviews.exists()  # ตรวจสอบว่ามีการรีวิวหรือไม่

        context = {
            'order': order,
            'payments': payments,
            'shipping_address': shipping_address,  # เพิ่มที่อยู่การจัดส่งใน context
            'is_reviewed': is_reviewed,  # ส่งค่าตรวจสอบการรีวิวไปยัง template
        }
        
        return render(request, 'profiles/buying/order-detail.html', context)

class SellingDetailView(LoginRequiredMixin, View):
    login_url = '/login/'
    
    def get(self, request, selling_id):
        # ดึงข้อมูลการขายที่ตรงกับ selling_id
        sale = get_object_or_404(Sale, id=selling_id)

        # ดึงข้อมูลการชำระเงินที่เกี่ยวข้องกับคำสั่งซื้อนั้น
        payments = Payment.objects.filter(order__product=sale.product)  # ใช้ order__product แทนการใช้ sale

        # ดึงข้อมูล product ที่เกี่ยวข้อง
        product = sale.product  # ดึงข้อมูล product จาก sale

        # สร้างตัวแปรที่ใช้ใน template
        context = {
            'sale': sale,
            'payments': payments,
            'product': product,
        }

        return render(request, 'profiles/selling-detail.html', context)
    

class CartView(LoginRequiredMixin, View):
    """แสดงสินค้าที่อยู่ในตะกร้า"""
    
    def get(self, request):
        cart = get_object_or_404(Cart, user=request.user)  # รับตะกร้าของผู้ใช้
        cart_items = cart.items.all()  # ดึงรายการสินค้าจากตะกร้า
        
        # คำนวณจำนวนรวมของสินค้าในตะกร้า
        total_quantity = sum(item.quantity for item in cart_items)  
        
        # คำนวณจำนวนเงินรวมทั้งหมด
        total_amount = sum(item.product.price * item.quantity for item in cart_items)

        # สร้าง context สำหรับส่งข้อมูลไปยัง template
        context = {
            'cart_items': cart_items,
            'total_quantity': total_quantity,
            'total_amount': total_amount,  # เพิ่มจำนวนเงินรวมเข้าไปใน context
        }
        
        return render(request, 'cart.html', context)  # แสดงผลหน้าตะกร้า

class AddToCartView(LoginRequiredMixin, View):
    """เพิ่มสินค้าในตะกร้า"""
    
    def post(self, request, product_id):
        # รับหรือสร้างตะกร้าสินค้าสำหรับผู้ใช้
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        # ค้นหาสินค้าโดยใช้ product_id
        product = get_object_or_404(Product, id=product_id)
        
        # รับหรือสร้างรายการในตะกร้า
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        
        # เพิ่มจำนวนถ้าสินค้าอยู่ในตะกร้าแล้ว
        if not created:
            cart_item.quantity = 1 
        
        # บันทึกการเปลี่ยนแปลง
        cart_item.save()

        # ส่งคืนการเปลี่ยนเส้นทางไปยังหน้าตะกร้า
        return redirect('cart')  # ส่งคืนวัตถุ HttpResponse

class RemoveFromCartView(LoginRequiredMixin, View):
    """Remove an item from the cart."""

    def post(self, request, item_id):
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        cart_item.delete()  # Remove the item from the cart

        return redirect('cart')  # Redirect back to the cart page

class ClearCartView(LoginRequiredMixin, View):
    """Clear all items from the cart."""

    def post(self, request):
        # รับตะกร้าของผู้ใช้
        cart = Cart.objects.filter(user=request.user).first()

        if cart:
            # ลบรายการในตะกร้า
            cart.items.all().delete()

        # Redirect ไปยังหน้าอื่น (เช่น หน้าแสดงตะกร้าหรือหน้าแรก)
        return redirect('cart')  # เปลี่ยน 'cart_view' เป็น URL name ที่ต้องการ
    

