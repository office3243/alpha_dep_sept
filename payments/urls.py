from django.conf.urls import url
from . import views

app_name = 'payments'

urlpatterns = [

    url(r'^paytm/create_payment/(?P<txn_id>[0-9a-zA-z-]+)/$', views.create_payment, name='paytm_create_payment'),
    url(r'^paytm/response/$', views.response, name='paytm_response'),

]