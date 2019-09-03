from django import forms
from .models import Order


class OrderPlaceForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = ("line_1", "line_2", "locality", "zip_code", "phone", "user_text", "receiver_name")
