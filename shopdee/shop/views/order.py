from django.shortcuts import get_object_or_404, render
from django.views import View
from django.db.models import Q
from shop.models import Order, Payment, ProductReview
from shop.mixins import ShopLoginRequiredMixin

class OrderDetailView(ShopLoginRequiredMixin, View):
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


class BuyingView(ShopLoginRequiredMixin, View):
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