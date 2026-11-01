from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

from cart.models import Favorite
from catalog.models import Product
from .forms import CustomUserCreationForm, UserProfileForm

def _migrate_session_favorites(request, user):
    session_favs = request.session.get('favorites', [])
    if session_favs:
        for product_id in session_favs:
            product = Product.objects.filter(id=product_id, is_available=True).first()
            if product:
                Favorite.objects.get_or_create(user=user, product=product)
        request.session['favorites'] = []
        request.session.modified = True


def register_view(request):
    if request.user.is_authenticated:
        return redirect('catalog:product_list')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            login(request, user, backend='users.backends.EmailOrUsernameModelBackend')

            _migrate_session_favorites(request, user)

            messages.success(request, f"Добро пожаловать, {user.first_name}! Регистрация прошла успешно.")
            return redirect('catalog:product_list')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('catalog:product_list')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            _migrate_session_favorites(request, user)

            messages.success(request, f"С возвращением, {user.first_name or user.username}!")
            next_url = request.GET.get('next', 'catalog:product_list')
            return redirect(next_url)
        else:
            messages.error(request, "Неверное имя пользователя/email или пароль.")
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "Вы вышли из учетной записи.")
    return redirect('catalog:product_list')


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Данные вашего профиля успешно обновлены!")
            return redirect('users:profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'users/profile.html', {'form': form})

from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash


@login_required
def password_change_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Ваш пароль был успешно изменен!")
            return redirect('users:profile')
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки при вводе пароля.")
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'users/password_change.html', {'form': form})