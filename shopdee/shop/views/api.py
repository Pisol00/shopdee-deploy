import json
import os
from django.conf import settings
from django.http import JsonResponse
from django.views import View
from shop.mixins import ShopLoginRequiredMixin

class GetDistrictsView(ShopLoginRequiredMixin, View):
    """API View สำหรับดึงข้อมูลอำเภอตามรหัสจังหวัด"""
    
    def get(self, request, province_id):
        district_file = os.path.join(settings.BASE_DIR, 'shop', 'data', 'thai_district.json')

        with open(district_file, encoding='utf-8') as f:
            districts = json.load(f)

        # กรองอำเภอตามรหัสจังหวัด
        filtered_districts = [d for d in districts if d['province_id'] == province_id]

        return JsonResponse({'districts': filtered_districts})


class GetSubdistrictsView(ShopLoginRequiredMixin, View):
    """API View สำหรับดึงข้อมูลตำบลตามรหัสอำเภอ"""
    
    def get(self, request, district_id):
        subdistrict_file = os.path.join(settings.BASE_DIR, 'shop', 'data', 'thai_subdistrict.json')

        with open(subdistrict_file, encoding='utf-8') as f:
            subdistricts = json.load(f)

        # กรองตำบลตามรหัสอำเภอ
        filtered_subdistricts = [s for s in subdistricts if s['district_id'] == district_id]

        return JsonResponse({'subdistricts': filtered_subdistricts})