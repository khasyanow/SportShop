from .cart import Cart
from .models import Favorite


def cart(request):
    cart_obj = Cart(request)
    # Список ID товаров, которые уже лежат в корзине (числа)
    cart_product_ids = [int(p_id) for p_id in cart_obj.cart.keys() if str(p_id).isdigit()]
    return {
        'cart': cart_obj,
        'cart_product_ids': cart_product_ids
    }


def favorites(request):
    if request.user.is_authenticated:
        fav_ids = list(Favorite.objects.filter(user=request.user).values_list('product_id', flat=True))
    else:
        fav_ids = request.session.get('favorites', [])
    return {'favorite_product_ids': fav_ids}