from django import forms
from django.contrib.auth.forms import UserCreationForm
from . models import User
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import password_validation

USER_MODEL = User


class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(max_length=13, widget=forms.TextInput(attrs={"class": "input-medium bfh-phone", "data-format": "+91dddddddddd", "placeholder": "+91987654321"}))


class RegisterForm(UserCreationForm):
    phone = forms.CharField(max_length=13, widget=forms.TextInput(attrs={"class": "input-medium bfh-phone", "data-format": "+91dddddddddd", "placeholder": "+91987654321"}))

    class Meta:
        model = User
        fields = ('phone', 'email', 'password1', 'password2',)


class PasswordResetForm(forms.Form):

    phone = forms.CharField(max_length=13, min_length=13, widget=forms.TextInput(attrs={"class": "input-medium bfh-phone", "data-format": "+91dddddddddd", "placeholder": "+91987654321"}))

    class Meta:
        fields = ('phone', )


class PasswordResetNewForm(forms.Form):

    otp = forms.IntegerField()
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 == password2:
            return self.cleaned_data
        else:
            raise ValidationError("Both password must be same.")

    def _post_clean(self):
        super()._post_clean()
        password = self.cleaned_data.get('password2')
        if password:
            try:
                password_validation.validate_password(password)
            except forms.ValidationError as error:
                self.add_error('password2', error)

    class Meta:
        fields = ('otp', 'password1', 'password2')


class OTPForm(forms.Form):
    otp = forms.IntegerField(widget=forms.NumberInput(attrs={"length": 6}))

    class Meta:
        fields = ('otp', )


class ProfileUpdateForm(forms.ModelForm):

    class Meta:
        model = USER_MODEL
        fields = ('first_name', 'last_name', 'email')
