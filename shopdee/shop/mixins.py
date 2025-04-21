from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Min
from django.shortcuts import get_object_or_404
from .models import Collection, Product
from .utils import get_starting_price, get_reviews_for_collection, get_random_collections

class CollectionDataMixin:
    """Mixin สำหรับ views ที่ต้องใช้ข้อมูลจากคอลเลกชัน"""
    
    def get_collection_context(self, collection_id):
        """
        รับข้อมูลคอลเลกชันและสร้าง context ที่ใช้บ่อยสำหรับเทมเพลต
        
        Args:
            collection_id: ID ของคอลเลกชัน
            
        Returns:
            dictionary: ข้อมูล context สำหรับเทมเพลต
        """
        collection = get_object_or_404(Collection, pk=collection_id)
        
        # ดึงข้อมูลราคา
        min_price = collection.product_set.aggregate(Min('price'))['price__min']
        new_product_price = collection.product_set.filter(condition='brand_new').aggregate(Min('price'))['price__min']
        
        # ดึงข้อมูลยอดขายล่าสุด
        last_sale = collection.product_set.filter(orders__isnull=False).order_by('-orders__date').first()
        last_sale_price = last_sale.price if last_sale else None
        
        # ดึงรูปภาพของคอลเลกชัน
        images = collection.images.all()
        primary_image = images.filter(is_primary=True).first()
        
        # ดึงรีวิวและคอลเลกชันอื่นๆ ที่แนะนำ
        reviews_with_ratings = get_reviews_for_collection(collection)
        random_collections = get_random_collections(collection)
        
        context = {
            'collection': collection,
            'min_price': min_price,
            'new_product_price': new_product_price,
            'last_sale_price': last_sale_price,
            'images': images,
            'primary_image': primary_image,
            'reviews_with_ratings': reviews_with_ratings,
            'random_collections': random_collections,
        }
        
        return context


class ShopLoginRequiredMixin(LoginRequiredMixin):
    """LoginRequiredMixin ที่กำหนด login_url"""
    login_url = "/login/"