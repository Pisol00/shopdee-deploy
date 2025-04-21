import random
from django.db.models import Min, Count
from .models import Collection, Product, ProductReview

def get_starting_price(collection):
    """
    คำนวณราคาต่ำสุดของคอลเลกชัน
    คืนค่าราคาต่ำสุดหรือ "N/A" หากไม่มีสินค้า
    """
    result = Product.objects.filter(collection=collection).aggregate(Min('price'))
    starting_price = result.get('price__min')
    
    return starting_price if starting_price is not None else "N/A"


def attach_collection_data(collections):
    """
    เพิ่มข้อมูลราคาและรูปภาพให้กับวัตถุ collection
    
    Args:
        collections: QuerySet หรือ list ของวัตถุ Collection
        
    Returns:
        None (แก้ไขวัตถุโดยตรง)
    """
    for collection in collections:
        # เพิ่มราคาเริ่มต้น
        collection.starting_price = get_starting_price(collection)
        
        # เพิ่มภาพหลัก
        collection.primary_image = collection.images.filter(is_primary=True).first()


def get_reviews_for_collection(collection):
    """
    ดึงรีวิวสำหรับสินค้าในคอลเลกชันพร้อมการจัดรูปแบบดาว
    
    Args:
        collection: วัตถุ Collection
        
    Returns:
        List of tuples: (review, formatted_rating)
    """
    reviews = ProductReview.objects.filter(product__collection=collection).order_by('-review_date')

    def get_star_rating(rating):
        full_stars = '★' * rating
        empty_stars = '☆' * (5 - rating)
        return full_stars + empty_stars

    ratings = [get_star_rating(review.rating) for review in reviews]
    return list(zip(reviews, ratings))


def get_random_collections(current_collection, limit=4):
    """
    ดึงคอลเลกชันแบบสุ่ม ยกเว้นคอลเลกชันปัจจุบัน
    
    Args:
        current_collection: วัตถุ Collection ที่ต้องการยกเว้น
        limit: จำนวนคอลเลกชันสูงสุดที่ต้องการ
        
    Returns:
        รายการของวัตถุ Collection พร้อมคุณสมบัติเพิ่มเติม
    """
    collections = list(Collection.objects.exclude(id=current_collection.id)
                      .prefetch_related('images'))
    
    if not collections:
        return []

    # สุ่มเลือกคอลเลกชัน
    random_collections = random.sample(collections, min(limit, len(collections)))

    # เพิ่มข้อมูลภาพและราคาให้กับคอลเลกชัน
    for collection in random_collections:
        collection.primary_image = collection.images.filter(is_primary=True).first()
        collection.starting_price = get_starting_price(collection)

    return random_collections


def get_most_popular_collections(limit=5):
    """
    ดึงคอลเลกชันยอดนิยมตามจำนวนคำสั่งซื้อ
    
    Args:
        limit: จำนวนคอลเลกชันสูงสุดที่ต้องการ
        
    Returns:
        QuerySet ของวัตถุ Collection พร้อมคุณสมบัติเพิ่มเติม
    """
    collections = Collection.objects.annotate(
        num_orders=Count('product__orders')
    ).order_by('-num_orders')[:limit]
    
    attach_collection_data(collections)
    return collections