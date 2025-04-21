from django import forms
from django.contrib.auth.models import User
from shop.models import Address

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['recipient_name', 'phone_number', 'address_line1', 'address_line2', 
                  'subdistrict', 'district', 'province', 'postal_code']
        labels = {
            'recipient_name': 'Recipient Name',
            'phone_number': 'Phone Number',
            'address_line1': 'Address Line 1',
            'address_line2': 'Address Line 2',
            'subdistrict': 'Subdistrict',
            'district': 'District',
            'province': 'Province',
            'postal_code': 'Postal Code',
        }

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not phone_number.isdigit() or len(phone_number) != 10:
            raise forms.ValidationError("Phone number must be 10 digits.")
        return phone_number

    def clean_postal_code(self):
        postal_code = self.cleaned_data.get('postal_code')
        if not postal_code.isdigit() or len(postal_code) != 5:
            raise forms.ValidationError("Postal code must be 5 digits.")
        return postal_code


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Email', 
                'readonly': 'readonly', 
                'style': 'background-color: #e9ecef; color: #495057; cursor: default;'
            }),
        }
    
    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not first_name.isalpha():
            raise forms.ValidationError("First name should only contain letters.")
        if not first_name.istitle():
            raise forms.ValidationError("First name should start with an uppercase letter.")
        return first_name
    
    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if not last_name.isalpha():
            raise forms.ValidationError("Last name should only contain letters.")
        if not last_name.istitle():
            raise forms.ValidationError("Last name should start with an uppercase letter.")
        return last_name


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput, label="Old Password", required=True)
    new_password = forms.CharField(widget=forms.PasswordInput, label="New Password", required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm New Password", required=True)

    def __init__(self, user, data=None):
        super().__init__(data=data)
        self.user = user  # เก็บ instance ของ user

    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):
            raise forms.ValidationError("Old password is incorrect.")
        return old_password

    def clean_new_password(self):
        new_password = self.cleaned_data.get('new_password')
        if len(new_password) < 8:
            raise forms.ValidationError("New password must be at least 8 characters long.")
        return new_password

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password and confirm_password and new_password != confirm_password:
            self.add_error('confirm_password', "New passwords do not match.")
            self.add_error('new_password', "New passwords do not match.")
            
        return cleaned_data