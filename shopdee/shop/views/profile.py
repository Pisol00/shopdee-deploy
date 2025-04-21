from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from shop.forms import EditProfileForm, ChangePasswordForm
from shop.mixins import ShopLoginRequiredMixin

class ProfileView(ShopLoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        context = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
        }
        return render(request, "profiles/profile/profile.html", context)


class EditProfileView(ShopLoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        form = EditProfileForm(instance=user)
        return render(request, 'profiles/profile/editprofile.html', {'form': form})

    def post(self, request):
        user = request.user
        form = EditProfileForm(request.POST, instance=user)

        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')
        else:
            messages.error(request, "There was an error updating your profile.")
        
        return render(request, 'profiles/profile/editprofile.html', {'form': form})


class ChangePasswordView(ShopLoginRequiredMixin, View):
    def get(self, request):
        form = ChangePasswordForm(user=request.user)
        return render(request, 'profiles/change_password.html', {'form': form})

    def post(self, request):
        form = ChangePasswordForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = request.user
            new_password = form.cleaned_data.get('new_password')

            # ตั้งค่ารหัสผ่านใหม่
            user.set_password(new_password)
            user.save()

            # อัปเดต session auth hash เพื่อให้ผู้ใช้ไม่ต้องล็อกอินใหม่
            update_session_auth_hash(request, user)

            messages.success(request, "Your password was successfully updated!")
            return redirect('change_password')
        
        messages.error(request, "There was an error updating your password.")
        return render(request, 'profiles/change_password.html', {'form': form})