from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib import messages
from catalog.models import Product
from .cart import Cart
from .models import Favorite


def cart_detail(request):
    cart = Cart(request)
    return render(request, 'cart/cart_detail.html', {'cart': cart})


@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    cart.add(product=product, quantity=quantity)

    # Если запрос асинхронный (AJAX) — отдаем JSON
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('ajax'):
        return JsonResponse({
            'success': True,
            'cart_total_items': len(cart),
            'cart_total_price': f"{float(cart.get_total_price()):,.2f}".replace(',', ' '),
            'message': f"«{product.name}» добавлен в корзину!"
        })

    return redirect('cart:cart_detail')


@require_POST
def cart_update_quantity(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)

    try:
        quantity = int(request.POST.get('quantity', 1))
    except (ValueError, TypeError):
        quantity = 1

    # Защита: не меньше 1 и не больше остатка на складе
    if quantity > product.stock:
        quantity = product.stock
    elif quantity < 1:
        quantity = 1

    cart.add(product=product, quantity=quantity, override_quantity=True)

    # Расчет суммы конкретной позиции
    item_total = float(product.price * quantity)

    return JsonResponse({
        'success': True,
        'quantity': quantity,
        'item_total_price': f"{item_total:,.2f}".replace(',', ' ') + ' ₽',
        'cart_total_price': f"{float(cart.get_total_price()):,.2f}".replace(',', ' ') + ' ₽',
        'cart_total_items': len(cart)
    })


@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart:cart_detail')


def favorite_list(request):
    if request.user.is_authenticated:
        favorites = Favorite.objects.filter(user=request.user).select_related('product')
        products = [fav.product for fav in favorites]
    else:
        fav_ids = request.session.get('favorites', [])
        products = Product.objects.filter(id__in=fav_ids, is_available=True)

    return render(request, 'cart/favorites.html', {'products': products})


def favorite_toggle(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product_id = int(product_id)
    is_favorite = False

    if request.user.is_authenticated:
        fav_item = Favorite.objects.filter(user=request.user, product=product).first()
        if fav_item:
            fav_item.delete()
            is_favorite = False
        else:
            Favorite.objects.create(user=request.user, product=product)
            is_favorite = True
        total_favorites = Favorite.objects.filter(user=request.user).count()
    else:
        favorites = request.session.get('favorites', [])
        if product_id in favorites:
            favorites.remove(product_id)
            is_favorite = False
        else:
            favorites.append(product_id)
            is_favorite = True
        request.session['favorites'] = favorites
        request.session.modified = True
        total_favorites = len(favorites)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'is_favorite': is_favorite,
            'total_favorites': total_favorites
        })

    return redirect(request.META.get('HTTP_REFERER', 'catalog:product_list'))