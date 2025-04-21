from django.shortcuts import render
from django.views import View
from django.db.models import Q, Min, Count
from shop.models import Brand, Collection, Category
from shop.utils import attach_collection_data, get_most_popular_collections

class HomePageView(View):
    def get(self, request):
        brands = Brand.objects.all()
        
        # แสดงคอลเลคชั่นล่าสุด 3 อันพร้อมราคาต่ำสุด
        collections = self.get_latest_collections(3)
        
        # คำนวณจำนวนคำสั่งซื้อในแต่ละคอลเล็กชัน
        most_popular_collections = get_most_popular_collections(3)
        
        # เตรียมข้อมูลสำหรับ rendering
        context = {
            'brands': brands,
            'collections': collections,
            'most_popular_collections': most_popular_collections,
        }
        return render(request, "homepage.html", context)

    def get_latest_collections(self, limit):
        """ดึงคอลเล็กชันล่าสุดพร้อมราคาต่ำสุด"""
        collections = Collection.objects.all().order_by('-created_at')[:limit]
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

        # ใช้ filter ตาม price ranges
        if price_ranges:
            price_filter = Q()
            for price_range in price_ranges:
                if '-' in price_range:
                    min_max = price_range.split('-')
                    min_price = float(min_max[0]) if min_max[0] else 0
                    max_price = float(min_max[1]) if len(min_max) > 1 and min_max[1] else None

                    if max_price is not None:
                        price_filter |= Q(product__price__gte=min_price, product__price__lte=max_price)
                    else:
                        price_filter |= Q(product__price__gte=min_price)
                else:
                    min_price = float(price_range)
                    price_filter |= Q(product__price__gte=min_price)
            collections = collections.filter(price_filter)

        # ใช้ filter ตามหมวดหมู่
        if selected_categories:
            collections = collections.filter(category__id__in=selected_categories)

        # ใช้ filter ตามแบรนด์
        if selected_brands:
            collections = collections.filter(brand__id__in=selected_brands)

        # สร้าง mapping ของ categories
        category_map = {category.id: category.name for category in categories}

        # เพิ่มข้อมูลภาพและหมวดหมู่ให้กับคอลเลกชัน
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