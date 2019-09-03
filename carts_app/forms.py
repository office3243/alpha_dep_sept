from django import forms
from .models import CartItem


class CartItemAddForm(forms.ModelForm):

    class Meta:
        model = CartItem
        fields = ("product", "quantity", "user_file")
