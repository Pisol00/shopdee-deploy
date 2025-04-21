from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from django.contrib import messages
from django.db import transaction
from shop.models import Collection, Product, Address, Order, Payment, Cart
from shop.mixins import ShopLoginRequiredMixin

class ProductCheckoutView(ShopLoginRequiredMixin, View):
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
        from shop.models import UsedProductImage
        product_images = UsedProductImage.objects.filter(product=product)
        
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
            messages.error(request, f"There was an error processing your order: {str(e)}")
            return redirect(request.path)


class PaymentSuccessView(ShopLoginRequiredMixin, View):
    def get(self, request, payment_id):
        payment = Payment.objects.get(id=payment_id)
        order = Order.objects.get(id=payment.order.id) 

        return render(request, './products/buy/payment_success.html', {
            'payment': payment,
            'order': order
        })