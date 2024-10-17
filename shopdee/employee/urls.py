from django.urls import path
from .views import *

urlpatterns = [
    path('employees/', EmployeeDashboardView.as_view(), name='employee_dashboard'),  # เปลี่ยนชื่อ URL เพื่อความชัดเจน
    path('collection/add/', CollectionAddPageView.as_view(), name='add_collection'),
    path('brand/add/', BrandAddView.as_view(), name='add_brand'),
    path('seller/add/', AddSellerView.as_view(), name='add_seller'),
    path('seller/remove', RemoveSellerView.as_view(), name='remove_seller'),  # URL สำหรับการลบ
]
