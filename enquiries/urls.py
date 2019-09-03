from django.conf.urls import url
from . import views

app_name = "enquiries"

urlpatterns = [
    url(r'^add/$', views.add_enquiry, name="add_enquiry"),
]
