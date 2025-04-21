from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from django.http import JsonResponse
from shop.models import Wishlist, Collection
from shop.mixins import ShopLoginRequiredMixin

class WishListView(ShopLoginRequiredMixin, View):
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


class AddToWishlistView(ShopLoginRequiredMixin, View):
    def get(self, request, collection_id):
        """เพิ่มสินค้าลงในรายการโปรด (wishlist) หรือตรวจสอบสถานะ"""
        collection = get_object_or_404(Collection, id=collection_id)
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)

        # ตรวจสอบว่าสินค้านั้นอยู่ใน Wishlist อยู่แล้วหรือไม่
        if collection in wishlist.collections.all():
            return JsonResponse({'status': 'already_added'})
        
        # ถ้ายังไม่มีใน Wishlist ให้เพิ่ม
        wishlist.collections.add(collection)
        return JsonResponse({'status': 'added'})


class RemoveFromWishlistView(ShopLoginRequiredMixin, View):
    def post(self, request, collection_id):
        """ลบสินค้าออกจากรายการโปรด (wishlist)"""
        wishlist = get_object_or_404(Wishlist, user=request.user)
        collection = get_object_or_404(Collection, id=collection_id)
        
        # ลบคอลเลกชันออกจาก wishlist
        wishlist.collections.remove(collection)
        
        return redirect('wishlist')