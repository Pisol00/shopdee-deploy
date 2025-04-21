import json
import os
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.db import transaction, IntegrityError
from django.db.models.deletion import ProtectedError
from shop.models import Address
from shop.forms import AddressForm
from shop.mixins import ShopLoginRequiredMixin

class AddressView(ShopLoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        addresses = Address.objects.filter(user=user)
        context = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'addresses': addresses
        }
        return render(request, "profiles/addresses/address.html", context)


class NewAddressView(ShopLoginRequiredMixin, View):
    def get(self, request):
        user = request.user

        # โหลดข้อมูลจังหวัด อำเภอ ตำบล
        province_file = os.path.join(settings.BASE_DIR, 'shop', 'data', 'thai_province.json')
        district_file = os.path.join(settings.BASE_DIR, 'shop', 'data', 'thai_district.json')
        subdistrict_file = os.path.join(settings.BASE_DIR, 'shop', 'data', 'thai_subdistrict.json')

        with open(province_file, encoding='utf-8') as f:
            provinces = json.load(f)
        with open(district_file, encoding='utf-8') as f:
            districts = json.load(f)
        with open(subdistrict_file, encoding='utf-8') as f:
            subdistricts = json.load(f)

        #เรียงลำดับตามตัวอักษร A-Z
        provinces = sorted(provinces, key=lambda x: x['name_en'])
        districts = sorted(districts, key=lambda x: x['name_en'])
        subdistricts = sorted(subdistricts, key=lambda x: x['name_en'])

        form = AddressForm()
        context = {
            'form': form,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'provinces': provinces,
            'districts': districts,
            'subdistricts': subdistricts,
        }
        return render(request, "profiles/addresses/newaddress.html", context)

    def post(self, request):
        user = request.user
        form = AddressForm(request.POST)

        if form.is_valid():
            address = form.save(commit=False)
            address.user = user
            
            address.province = request.POST.get('province_name')
            address.district = request.POST.get('district_name')
            address.subdistrict = request.POST.get('subdistrict_name')
            
            address.save()
            messages.success(request, "New address has been saved successfully!") 
            return redirect('address')
        
        return render(request, "profiles/addresses/newaddress.html", {'form': form})


class EditAddressView(ShopLoginRequiredMixin, View):
    def load_location_data(self):
        """Load location data from JSON files."""
        province_file = os.path.join(settings.BASE_DIR, 'shop', 'data', 'thai_province.json')
        district_file = os.path.join(settings.BASE_DIR, 'shop', 'data', 'thai_district.json')
        subdistrict_file = os.path.join(settings.BASE_DIR, 'shop', 'data', 'thai_subdistrict.json')

        with open(province_file, encoding='utf-8') as f:
            provinces = json.load(f)
        with open(district_file, encoding='utf-8') as f:
            districts = json.load(f)
        with open(subdistrict_file, encoding='utf-8') as f:
            subdistricts = json.load(f)

        return provinces, districts, subdistricts

    def get(self, request, address_id):
        user = request.user
        try:
            address = Address.objects.get(pk=address_id, user=user)
        except Address.DoesNotExist:
            messages.error(request, "Address not found.")
            return redirect('address')  # Redirect to address list if not found

        provinces, districts, subdistricts = self.load_location_data()
        form = AddressForm(instance=address)

        context = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'form': form,
            'provinces': provinces,
            'districts': districts,
            'subdistricts': subdistricts
        }
        return render(request, "profiles/addresses/editaddress.html", context)

    def post(self, request, address_id):
        try:
            address = Address.objects.get(pk=address_id, user=request.user)
        except Address.DoesNotExist:
            messages.error(request, "Address not found.")
            return redirect('address')

        form = AddressForm(request.POST, instance=address)

        if form.is_valid():
            form.save()
            messages.success(request, "Address updated successfully!")
            return redirect('address')
        else:
            messages.error(request, "There were errors in your submission.")

        provinces, districts, subdistricts = self.load_location_data()

        context = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'form': form,
            'provinces': provinces,
            'districts': districts,
            'subdistricts': subdistricts
        }
        return render(request, "profiles/addresses/editaddress.html", context)


class DeleteAddressView(ShopLoginRequiredMixin, View):
    def post(self, request, address_id):
        address = get_object_or_404(Address, pk=address_id, user=request.user)
        
        try:
            with transaction.atomic():  # ใช้ transaction เพื่อให้มั่นใจในการดำเนินการ
                address.delete()
                messages.success(request, "Address deleted successfully.")
        except ProtectedError:
            messages.error(request, "Cannot delete this address because it is being used in an order.")
        except IntegrityError:
            messages.error(request, "An integrity error occurred while trying to delete the address.")
        
        return redirect('address')