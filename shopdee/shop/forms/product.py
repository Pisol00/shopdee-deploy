from django import forms
from shop.models.product import Category, Brand, Collection, Product, CollectionImage, UsedProductImage

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
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


class CollectionForm(forms.ModelForm):
    class Meta:
        model = Collection
        fields = ['category', 'brand', 'name', 'colorway']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'brand': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'colorway': forms.TextInput(attrs={'class': 'form-control'}),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'collection', 'size_clothing', 'size_shoes', 'price', 'quantity',
            'has_defect', 'condition'
        ]
        widgets = {
            'collection': forms.Select(attrs={'class': 'form-control'}),
            'size_clothing': forms.Select(attrs={'class': 'form-control'}),
            'size_shoes': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'has_defect': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'condition': forms.Select(attrs={'class': 'form-control'}),
        }


class CollectionImageForm(forms.ModelForm):
    class Meta:
        model = CollectionImage
        fields = ['collection', 'image_url', 'is_primary']
        widgets = {
            'collection': forms.Select(attrs={'class': 'form-control'}),
            'image_url': forms.URLInput(attrs={'class': 'form-control'}),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class UsedProductImageForm(forms.ModelForm):
    class Meta:
        model = UsedProductImage
        fields = ['image']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control'})
        }