from django import template
from products.models import Category
from carts_app.views import get_request_cart
from orders.models import Order

register = template.Library()


@register.simple_tag
def get_category_url_by_name_contains(name):
    qs = Category.objects.filter(name__icontains=name)
    if qs.exists():
        return qs.first().get_absolute_url
    else:
        return "#"


@register.simple_tag
def get_request_cart_amount(request):
    amount = int(get_request_cart(request).amount)

    return amount


@register.simple_tag
def get_request_cart_items_count(request):
    return get_request_cart(request).cartitem_set.count()


@register.simple_tag
def get_pending_orders_count(request):
    if request.user.is_authenticated:
        return request.user.order_set.exclude(status__in=("SH", "CN")).count()
