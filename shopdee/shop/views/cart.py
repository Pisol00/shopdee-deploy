from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from django.contrib import messages
from shop.models import Cart, CartItem, Product, Address
from shop.mixins import ShopLoginRequiredMixin

class CartView(ShopLoginRequiredMixin, View):
    """แสดงสินค้าที่อยู่ในตะกร้า"""
    
    def get(self, request):
        cart = get_object_or_404(Cart, user=request.user)
        cart_items = cart.items.all()  # ดึงรายการสินค้าทั้งหมดในตะกร้า
        
        # คำนวณจำนวนรวมของสินค้าที่อยู่ในตะกร้า
        total_quantity = sum(item.quantity for item in cart_items)  
        
        # คำนวณจำนวนเงินรวมทั้งหมดของสินค้า
        total_amount = sum(item.product.price * item.quantity for item in cart_items)
        
        context = {
            'cart_items': cart_items, 
            'total_quantity': total_quantity,
            'total_amount': total_amount,
        }
        
        return render(request, 'cart.html', context)


class AddToCartView(ShopLoginRequiredMixin, View):
    """เพิ่มสินค้าในตะกร้า"""
    
    def post(self, request, product_id):
        # รับตะกร้าสำหรับผู้ใช้
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        # ค้นหาสินค้าที่จะเพิ่มโดยใช้ product_id
        product = get_object_or_404(Product, id=product_id)
        
        # รับหรือสร้างรายการสินค้าในตะกร้า
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        
        # ถ้าสินค้าอยู่ในตะกร้าแล้ว ให้เพิ่มจำนวนเป็น 1
        if not created:
            cart_item.quantity = 1 
        
        cart_item.save()
        
        messages.success(request, "Product added to cart successfully!")
        return redirect('cart')


class RemoveFromCartView(ShopLoginRequiredMixin, View):
    """ลบสินค้าจากตะกร้า"""

    def post(self, request, item_id):
        # รับรายการสินค้าที่จะลบโดยใช้ item_id และตรวจสอบว่าอยู่ในตะกร้าของผู้ใช้นี้
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        cart_item.delete()  # ลบรายการสินค้าจากตะกร้า

        messages.success(request, "Item removed from cart successfully!")
        return redirect('cart')  # ส่งคืนไปยังหน้าตะกร้า


class ClearCartView(ShopLoginRequiredMixin, View):
    """ลบสินค้าทั้งหมดในตะกร้า"""

    def post(self, request):
        # รับตะกร้าของผู้ใช้
        cart = Cart.objects.filter(user=request.user).first()

        if cart:
            # ลบรายการทั้งหมดในตะกร้า
            cart.items.all().delete()
            messages.success(request, "Cart cleared successfully!")

        # เปลี่ยนเส้นทางไปยังหน้าตะกร้า
        return redirect('cart')


class CheckoutCartView(ShopLoginRequiredMixin, View):
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