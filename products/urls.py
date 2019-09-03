from django.conf.urls import url
from . import views


app_name = "products"

urlpatterns = [

    # url(r"^$", views.ProductListView.as_view(), name="list"),
    url(r"^$", views.ProductListFilterView.as_view(), name="list"),
    url(r"^category/list/(?P<id>[0-9]+)/$", views.CategoryProductListView.as_view(), name="category_products_list"),
    url(r"^category/list/$", views.CategoryListView.as_view(), name="category_list"),
    url(r"^detail/(?P<slug>[-\w]+)/$", views.ProductDetailView.as_view(), name="detail"),
    url(r"^search/$", views.search_items, name="search_items"),
    # url(r'^visiting_cards/$', views.ProductListFilterView.as_view(), name="visiting_cards"),
    # url(r'^/$', views.PenFilterView.as_view(), name="pens"),
    # url(r'^id_cards/$', views.ProductListFilterView.as_view(), name="id_cards"),
]
