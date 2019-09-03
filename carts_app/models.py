from django.db import models
from django.db.models.signals import post_save, m2m_changed, post_delete
from products.validators import validate_nonzero
from django.core.validators import ValidationError
from django.shortcuts import get_list_or_404
from django.http import Http404
import uuid
from django.urls import reverse_lazy
import decimal


class Cart(models.Model):

    user = models.OneToOneField("accounts.User", on_delete=models.CASCADE, blank=True, null=True)
    uuid = models.UUIDField(default=uuid.uuid4)
    updated_on = models.DateTimeField(auto_now=True)

    amount = models.DecimalField(max_digits=7, decimal_places=2, default=0.00)

    def __str__(self):
        return self.user.phone if self.user else str(self.uuid)

    def save(self, *args, **kwargs):
        amount = decimal.Decimal(0.00)
        for item in self.cartitem_set.all():
            amount += item.amount
        if self.amount != amount:
            self.amount = amount
        super().save()


# def assign_amount_(sender, instance, action, *args, **kwargs):
#     amount = 0
#     for item in instance.cartitem_set.all():
#         amount += item.amount
#     if instance.amount != amount:
#         instance.amount = amount
#         instance.save()
#
#
# m2m_changed.connect(assign_amount, sender=Cart.)


class CartItem(models.Model):
    product = models.ForeignKey("products.Product", models.PROTECT)
    rate = models.ForeignKey("products.Rate", on_delete=models.PROTECT, blank=True, null=True)
    quantity = models.PositiveSmallIntegerField(default=1, validators=[validate_nonzero])
    amount = models.DecimalField(max_digits=7, decimal_places=2, default=0.00)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, blank=True, null=True)
    user_file = models.FileField(upload_to="cartitems/user_files/", blank=True, null=True)

    def __str__(self):
        return "{} - {} X {} = {}".format(self.id, self.get_unit_rate, self.quantity, self.amount)

    @property
    def get_amount(self):
        return self.amount if hasattr(self, "amount") else "Unknown"

    @property
    def get_unit_rate(self):
        if self.rate is not None:
            return self.rate.per_piece_amount
        return "Unknown"

    @property
    def get_user_file_download_link(self):
        if self.user_file:
            return reverse_lazy("carts_app:user_file_download", kwargs={"id": self.id})
        else:
            return ""

    def clean(self):
        if self.product.category.is_rate_qty:
            allowed_quantities = self.product.rate_set.order_by("quantity").values_list("quantity", flat=True)
            if self.quantity not in allowed_quantities:
                raise ValidationError(
                    "Quantity Not Allowed"
                )
        else:
            qty = self.product.rate_set.order_by("quantity").first().quantity
            if self.quantity < qty:
                raise ValidationError(
                    "Minimum allowed quantity is {}".format(qty)
                )

    # def save(self, *args, **kwargs):
    #     if self.rate is not None and self.amount != 0.00:
    #         self.cart.save()
    #         super().save()


def assign_rate(sender, instance, *args, **kwargs):
    rate = instance.product.rate_set.filter(quantity__lte=instance.quantity).order_by("-quantity").first()
    if not hasattr(instance, "rate") or instance.rate != rate:
        instance.rate = rate
        instance.save()


def assign_amount(sender, instance, *args, **kwargs):
    if instance.rate is not None:
        try:
            amount = instance.quantity * instance.rate.per_piece_amount
            if instance.amount != amount:
                instance.amount = amount
                instance.save()
        except:
            instance.save()


def save_cart(sender, instance, *args, **kwargs):
    if instance.rate is not None and instance.amount != 0.00:
        try:
            instance.cart.save()
        except:
            pass


post_save.connect(assign_rate, sender=CartItem)
post_save.connect(assign_amount, sender=CartItem)
post_save.connect(save_cart, sender=CartItem)
post_delete.connect(save_cart, sender=CartItem)