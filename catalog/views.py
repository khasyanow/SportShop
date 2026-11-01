from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Category, Product, Sport
from django.db.models import Count
from orders.models import OrderItem

def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.filter(parent=None)
    products = Product.objects.filter(is_available=True)

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        subcategories = category.children.all()
        if subcategories.exists():
            products = products.filter(Q(category=category) | Q(category__in=subcategories))
        else:
            products = products.filter(category=category)

    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(sports__name__icontains=query)
        ).distinct()

    sport_name = request.GET.get('sport')
    if sport_name:
        products = products.filter(Q(sports__name__iexact=sport_name) | Q(sports__isnull=True)).distinct()

    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    if price_min:
        products = products.filter(price__gte=price_min)
    if price_max:
        products = products.filter(price__lte=price_max)

    sort = request.GET.get('sort', 'new')
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'name':
        products = products.order_by('name')
    else:
        products = products.order_by('-created_at')

    sports_qs = Sport.objects.filter(products__is_available=True).distinct()

    context = {
        'category': category,
        'categories': categories,
        'products': products,
        'sports': sports_qs,
        'current_sport': sport_name,
        'current_sort': sort,
        'price_min': price_min or '',
        'price_max': price_max or '',
        'query': query or '',
    }
    return render(request, 'catalog/product_list.html', context)


def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug, is_available=True)

    order_ids = OrderItem.objects.filter(product=product).values_list('order_id', flat=True)
    bought_together = Product.objects.filter(
        order_items__order_id__in=order_ids,
        is_available=True
    ).exclude(id=product.id).annotate(
        times_bought=Count('order_items')
    ).order_by('-times_bought')[:4]

    recommended_products = list(bought_together)

    if len(recommended_products) < 4:
        needed = 4 - len(recommended_products)
        exclude_ids = [p.id for p in recommended_products] + [product.id]

        similar_products = Product.objects.filter(
            category=product.category,
            is_available=True
        ).exclude(id__in=exclude_ids).order_by('-created_at')[:needed]

        recommended_products.extend(list(similar_products))

    if len(recommended_products) < 4:
        needed = 4 - len(recommended_products)
        exclude_ids = [p.id for p in recommended_products] + [product.id]

        latest_products = Product.objects.filter(
            is_available=True
        ).exclude(id__in=exclude_ids).order_by('-created_at')[:needed]

        recommended_products.extend(list(latest_products))

    context = {
        'product': product,
        'recommended_products': recommended_products,
    }
    return render(request, 'catalog/product_detail.html', context)

def contacts_view(request):
    return render(request, 'catalog/contacts.html')

