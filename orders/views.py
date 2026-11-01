from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from cart.cart import Cart
from .models import Order, OrderItem
from .forms import OrderCreateForm


@login_required
def order_create(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.warning(request, "Ваша корзина пуста. Нечего оформлять.")
        return redirect('catalog:product_list')

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                order = form.save(commit=False)
                order.user = request.user
                order.total_cost = cart.get_total_price()
                order.save()

                for item in cart:
                    product = item['product']
                    quantity = item['quantity']

                    if product.stock >= quantity:
                        product.stock -= quantity
                        product.save()
                    else:
                        messages.error(request, f"К сожалению, товара '{product.name}' недостаточно на складе.")
                        transaction.set_rollback(True)
                        return redirect('cart:cart_detail')

                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        price=item['price'],
                        quantity=quantity
                    )

                cart.clear()

            messages.success(request, f"Заявка №{order.id} успешно сформирована и передана менеджеру!")
            return render(request, 'orders/order_success.html', {'order': order})
    else:
        initial_data = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
            'phone': request.user.phone,
            'address': request.user.address,
        }
        form = OrderCreateForm(initial=initial_data)

    return render(request, 'orders/order_create.html', {'cart': cart, 'form': form})


@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'orders/order_list.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})