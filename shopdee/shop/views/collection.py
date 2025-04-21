from django.shortcuts import get_object_or_404, render
from django.views import View
from django.db.models import Min
from django.contrib.auth.mixins import LoginRequiredMixin
from shop.models import Collection
from shop.utils import get_reviews_for_collection, get_random_collections
from shop.mixins import CollectionDataMixin

class CollectionDetailView(LoginRequiredMixin, CollectionDataMixin, View):
    login_url = "/login/"
    
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
        images = collection.images.all()
        primary_image = images.filter(is_primary=True).first()
        
        # ดึงรีวิวสำหรับคอลเล็กชัน
        reviews_with_ratings = get_reviews_for_collection(collection)
        
        # ดึงคอลเล็กชันแบบสุ่มโดยไม่รวมคอลเล็กชันปัจจุบัน
        random_collections = get_random_collections(collection)

        # ตั้งราคาตั้งต้นสำหรับคอลเล็กชันแบบสุ่ม
        # (โน้ต: ฟังก์ชัน get_random_collections ในไฟล์ utils.py จะจัดการเรื่องนี้ให้แล้ว)
        
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