import requests
from .forms import RegisterForm, PasswordResetForm, PasswordResetNewForm, OTPForm, ProfileUpdateForm
from django.views.generic import TemplateView, ListView, FormView, View, DetailView, UpdateView
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from . import alert_messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from .models import User


API_KEY_2FA = settings.API_KEY_2FA

registeration_otp_template = "Registration_Template"

password_reset_otp_template = "Password_Reset_Template"


def register(request):
    form = RegisterForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "You have successfully registered and logged in.")
            if "next" in request.POST:
                return redirect(request.POST['next'])
            return redirect("portal:home")

    return render(request, "accounts/register.html", {"form": form})


def password_reset_otp_generate(request, user):
    request.session["user_session_id"] = str(user.id)
    otp_template = password_reset_otp_template
    if 'user_session_data' in request.session:
        del request.session['user_session_data']
    url = "http://2factor.in/API/V1/{API_KEY_2FA}/SMS/{phone}/AUTOGEN/{otp_template}".format(API_KEY_2FA=API_KEY_2FA,
                                                                                             phone=user.phone,
                                                                                             otp_template=otp_template)
    response = requests.request("GET", url)
    data = response.json()
    request.session['user_session_data'] = data['Details']
    messages.info(request, alert_messages.PASSWORD_RESET_OTP_SENT_MESSAGE)
    return redirect("accounts:password_reset_new")


def check_otp_2fa(otp, otp_session_data):
    url = "http://2factor.in/API/V1/{0}/SMS/VERIFY/{1}/{2}".format(API_KEY_2FA,
                                                                   otp_session_data, otp)
    response = requests.request("GET", url)
    data = response.json()
    return data['Status'] == "Success"


def password_reset_otp_resend(request):
    try:
        user = get_object_or_404(User, id=request.session.get('user_session_id'))
        return password_reset_otp_generate(request, user=user)
    except User.DoesNotExist:
        raise Http404("Bad Request")


@login_required
def password_change(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, alert_messages.PASSWORD_CHANGED_SUCCESS_MESSAGE)
            return redirect('portal:home')
        else:
            messages.error(request, alert_messages.FORM_INVALID_MESSAGE)
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/password_change.html', {
        'form': form
    })


class PasswordResetView(FormView):

    template_name = "accounts/password_reset.html"
    form_class = PasswordResetForm

    def form_valid(self, form):
        phone = form.cleaned_data.get('phone')
        try:
            user = User.objects.get(phone=phone)
            if user.is_active:
                return password_reset_otp_generate(self.request, user=user)
            else:
                messages.warning(self.request, alert_messages.USER_NON_ACTIVE_MESSAGE)
                return redirect("accounts:password_reset")
        except User.DoesNotExist:
            messages.warning(self.request, alert_messages.PHONE_NOT_REGISTERED_MESSAGE)
            return redirect("accounts:password_reset")


class PasswordResetNewView(FormView):

    template_name = "accounts/password_reset_new.html"
    form_class = PasswordResetNewForm

    def form_valid(self, form):
        otp = form.cleaned_data.get('otp')
        password1 = form.cleaned_data.get('password1')
        user = get_object_or_404(User, id=self.request.session.get('user_session_id'))

        otp_match = check_otp_2fa(otp=otp, otp_session_data=self.request.session['user_session_data'])
        if otp_match:
            user.set_password(password1)
            user.save()
            del self.request.session['user_session_id']
            del self.request.session['user_session_data']
            messages.success(self.request, "Password changed")
            login(self.request, user)
            return redirect("portal:home")
        else:
            messages.error(self.request, "please enter correct OTP!")
            return redirect("accounts:password_reset_new")


class ProfileUpdateView(LoginRequiredMixin, UpdateView):

    form_class = ProfileUpdateForm
    template_name = "accounts/profile_update.html"
    model = User
    success_url = reverse_lazy("accounts:profile_update")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, alert_messages.PROFILE_UPDATED_MESSAGE)
        return super().form_valid(form)
