from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.conf import settings
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r"", include("portal.urls", namespace="portal")),
    url(r"^accounts/", include("accounts.urls", namespace="accounts")),
    url(r"^cart/", include("carts_app.urls", namespace="carts")),
    url(r"^products/", include("products.urls", namespace="products")),
    url(r"^orders/", include("orders.urls", namespace="orders")),
    url(r"^payments/", include("payments.urls", namespace="payments")),
    url(r"^enquiries/", include("enquiries.urls", namespace="enquiries")),

    url(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT, 'show_indexes': settings.DEBUG})


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
