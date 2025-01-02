from django import forms
from django.contrib.auth.models import User
from shop.models import *

class CollectionForm(forms.ModelForm):
    class Meta:
        model = Collection
        fields = ['category', 'brand', 'name', 'colorway']  # รวมฟิลด์ทั้งหมดที่ต้องการในฟอร์ม
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'brand': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'colorway': forms.TextInput(attrs={'class': 'form-control'}),
        }

class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ['name', 'description', 'img_url']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter brand name'}),
            'description': forms.Textarea(attrs={'class': 'form-control description', 'placeholder': 'Enter brand description'}),
            'img_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Enter image URL (optional)'}),
        }
        
from django import forms
from django.contrib.auth.models import User

class SellerForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=User.objects.none(), required=True)

    class Meta:
        model = User
        fields = ['user']
