from django.conf.urls import url
from . import views


app_name = "carts_app"

urlpatterns = [
    url(r"^$", views.CartView.as_view(), name="cart_view"),
    # url(r"^item/add/$", views.ItemAddView.as_view(), name="item_add"),
    url(r"^item/add/$", views.item_add, name="item_add"),
    # url(r"^item/delete/$", views.item_delete, name="item_delete"),
    url(r"^item/delete/(?P<item_id>[0-9]+)/$", views.item_delete, name="item_delete"),
    url("^user_file/download/(?P<id>[0-9]+)/$", views.user_file_download, name="user_file_download"),
]
