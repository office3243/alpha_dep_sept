from django.conf.urls import url
from django.contrib.auth.views import LoginView, LogoutView, logout_then_login
from . import views
from .forms import CustomLoginForm


app_name = "accounts"

urlpatterns = [

    # url(r"^login/$", LoginView.as_view(template_name="accounts/login.html"), name="login"),

    url(r'^login/$', LoginView.as_view(template_name='accounts/login.html', authentication_form=CustomLoginForm),
        name='login'),
    url(r"^register/$", views.register, name="register"),
    url(r"^logout/$", logout_then_login, {"login_url": "/accounts/login/"}, name="logout"),

    url(r"^profile/$", views.ProfileUpdateView.as_view(), name='profile_update'),

    url(r"^password/change/$", views.password_change, name='password_change'),

    url(r"^password/reset/$", views.PasswordResetView.as_view(), name='password_reset'),

    url(r"^password/reset/new/$", views.PasswordResetNewView.as_view(), name='password_reset_new'),
    url(r"^password/reset/otp/resend/$", views.password_reset_otp_resend, name='password_reset_otp_resend'),


]