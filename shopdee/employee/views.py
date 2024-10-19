from django.views import View
from django.shortcuts import redirect, render
from shop.models import *
from .forms import *
from django.contrib.auth.models import Group, User
from django.db.models import Count
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin


from django.db.models import Count

class EmployeeDashboardView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'employee.view_employee_dashboard'
    login_url = "/login/"

    def get(self, request):
        collections_with_sales = Collection.objects.annotate(
            total_sales=Count('product__sales')
        ).order_by('-total_sales')
        # สร้างลิสต์เพื่อเก็บข้อมูลคอลเลกชันและขนาดที่ขายได้ดีที่สุด
        collection_data = []
        for collection in collections_with_sales:
            best_selling_size = self.get_best_selling_size(collection)
            collection_data.append({
                'collection': collection,
                'best_selling_size': best_selling_size,
            })

        total_orders = Order.objects.count()
        top_provinces = self.get_top_provinces()

        context = {
            'collections': collections_with_sales,
            'collection_data': collection_data,  # ใช้ collection_data แทน
            'sales_analytics': {
                'total_orders': total_orders,
                'top_provinces': top_provinces,
            },
            'wishlists': Wishlist.objects.all(),
        }

        return render(request, 'employee.html', context)

    def get_best_selling_size(self, collection):
        # เช็คว่า collection เป็นรองเท้าหรือเสื้อผ้า
        if collection.category.name == "Clothing":  # สมมติว่าใช้ชื่อ "Clothing" สำหรับเสื้อผ้า
            best_selling_size = Product.objects.filter(collection=collection) \
                .values('size_clothing').annotate(total_sales=Count('sales')).order_by('-total_sales').first()
            
            if best_selling_size:
                return best_selling_size['size_clothing']
        
        elif collection.category.name == "Shoes":  # สมมติว่าใช้ชื่อ "Shoes" สำหรับรองเท้า
            best_selling_size = Product.objects.filter(collection=collection) \
                .values('size_shoes').annotate(total_sales=Count('sales')).order_by('-total_sales').first()
            
            if best_selling_size:
                return best_selling_size['size_shoes']
        
        return None  # หากไม่พบขนาดที่ขายได้

    def get_top_provinces(self):
        top_provinces = Order.objects.values('shipping_address__province') \
            .annotate(order_count=Count('id')) \
            .order_by('-order_count')[:10]
        return top_provinces



class BrandAddView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'employee.add_brand'  # เปลี่ยน 'app_name' เป็นชื่อแอปของคุณ
    login_url = "/login/"

    def get(self, request):
        form = BrandForm()
        return render(request, 'brand-add.html', {'form': form})

    def post(self, request):
        form = BrandForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('brand_list')
        return render(request, 'brand-add.html', {'form': form})


class CollectionAddPageView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'employee.add_collection'  # เปลี่ยน 'app_name' เป็นชื่อแอปของคุณ
    login_url = "/login/"

    def get(self, request):
        form = CollectionForm()
        return render(request, 'collection-add.html', {'form': form})

    def post(self, request):
        form = CollectionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('collection_list')
        return render(request, 'collection-add.html', {'form': form})


class AddSellerView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'employee.add_seller'  # เปลี่ยน 'app_name' เป็นชื่อแอปของคุณ

    def get(self, request):
        context = self.get_users_context()
        return render(request, 'seller-add.html', context)

    def post(self, request):
        user_id = request.POST.get('user_id')
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                seller_group, created = Group.objects.get_or_create(name='Seller')
                user.groups.add(seller_group)
                return redirect('add_seller')
            except User.DoesNotExist:
                error = 'User not found.'
        else:
            error = 'No user selected.'

        return render(request, 'seller-add.html', self.get_users_context(error))

    def get_users_context(self, error=None):
        users_without_group = User.objects.exclude(groups__name='Seller')
        users_with_group = User.objects.filter(groups__name='Seller')
        return {
            'users_without_group': users_without_group,
            'users_with_group': users_with_group,
            'error': error,
        }


class RemoveSellerView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'employee.remove_seller'  # เปลี่ยน 'app_name' เป็นชื่อแอปของคุณ

    def post(self, request):
        user_id = request.POST.get('user_id')
        try:
            user = User.objects.get(id=user_id)
            seller_group = Group.objects.get(name='Seller')
            user.groups.remove(seller_group)
        except (User.DoesNotExist, Group.DoesNotExist):
            pass
        return redirect('add_seller')
