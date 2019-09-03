from django.conf.urls import url
from . import views
from django.contrib.auth.views import LoginView, LogoutView, logout_then_login


app_name = "portal"

urlpatterns = [

    url(r"^$", views.HomeView.as_view(), name="home"),
    url(r"^contact/$", views.ContactView.as_view(), name="contact"),
]
