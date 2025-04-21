from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import transaction
from shop.models import Collection, Product, Sale, UsedProductImage
from shop.mixins import ShopLoginRequiredMixin

class SellingView(ShopLoginRequiredMixin, View):
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


class SellingDetailView(ShopLoginRequiredMixin, View):
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


class SellDetailView(ShopLoginRequiredMixin, PermissionRequiredMixin, View):
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

    def post(self, request):
        try:
            collection_id = request.GET.get('collection_id')
            size = request.POST.get('size')
            has_defect = request.POST.get('has_defect')
            equipment = request.POST.get('equipment')
            price = request.POST.get('price')
            images = request.FILES.getlist('images')  # ดึงข้อมูลไฟล์รูปภาพทั้งหมด
            
            # ตรวจสอบค่าที่ได้รับจากแบบฟอร์ม
            if not size or not price:
                collection = Collection.objects.get(id=collection_id)
                return render(request, './products/sell/sell_detail.html', {
                    'error': 'Size and Price are required.',
                    'collection': collection
                })

            # เก็บข้อมูลลงใน session
            sell_data = {
                'collection_id': collection_id,
                'size': size,
                'has_defect': has_defect,
                'equipment': equipment,
                'price': price
            }
            request.session['sell_data'] = sell_data

            # เปลี่ยนเส้นทางไปยังหน้าสรุป
            return redirect('sell_summary')

        except Exception as e:
            collection = Collection.objects.get(id=collection_id)
            return render(request, './products/sell_detail.html', {
                'error': str(e),
                'collection': collection  # ส่งข้อมูลคอลเลกชันเพื่อใช้ในการแสดงผล
            })


class SellSummaryView(ShopLoginRequiredMixin, PermissionRequiredMixin, View):
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
        payment_method = request.POST.get('payment_method', 'bank_transfer')

        if not price:
            return self._render_summary_with_error(collection_id, sell_data, "ราคาจำเป็นต้องระบุ.")
        
        try:
            price = float(price)
        except ValueError:
            return self._render_summary_with_error(collection_id, sell_data, "รูปแบบราคาไม่ถูกต้อง.")

        collection = get_object_or_404(Collection, id=collection_id)
        
        # กำหนดขนาดตามประเภทของคอลเลกชัน
        size_clothing, size_shoes = self._get_sizes(collection, size)

        # รับภาพที่อัปโหลด
        uploaded_images = request.FILES.getlist('images')

        # เริ่มต้นการทำธุรกรรม
        try:
            with transaction.atomic():
                # สร้าง Product
                product = self._create_product(collection, size_clothing, size_shoes, price, has_defect, equipment)

                # บันทึกรูปภาพที่อัปโหลด
                for image in uploaded_images:
                    if not image.content_type.startswith('image/'):
                        return self._render_summary_with_error(collection_id, sell_data, "ไฟล์ที่อัปโหลดต้องเป็นภาพ.")
                    
                    UsedProductImage.objects.create(product=product, image=image)

                # สร้าง Sale
                Sale.objects.create(user=request.user, product=product, price=price)
                
                messages.success(request, "Successfully listed the product for sale!")
            
            return redirect('homepage')

        except Exception as e:
            return self._render_summary_with_error(collection_id, sell_data, "เกิดข้อผิดพลาดในการบันทึกข้อมูล: " + str(e))
    
    def _get_sizes(self, collection, size):
        """กำหนดขนาดตามประเภทของคอลเลกชัน."""
        if collection.category.name == 'Apparel':
            return size, None
        elif collection.category.name == 'Shoes':
            return None, size
        return None, None

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
        price = float(sell_data.get('price', 0))
        transaction_fee = price * 0.07
        processing_fee = price * 0.03
        total_payout = price - (transaction_fee + processing_fee)
        
        return render(
            request=self.request,
            template_name='./products/sell/sell_summary.html',
            context={
                'collection': collection,
                'error': error_message,
                'sell_data': sell_data,
                'transaction_fee': transaction_fee,
                'processing_fee': processing_fee,
                'total_payout': total_payout,
                'images': collection.images.all()
            }
        )