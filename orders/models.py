from django.db import models
from django.db.models import Aggregate, Sum, Q, Count
from django.urls import reverse_lazy
from accounts.models import User
from django.db.models.signals import m2m_changed, post_save
import random
import string
import decimal
import requests
from django.conf import settings
import json
from django.core.validators import FileExtensionValidator
from django.core.mail import send_mail


def txn_id_generator(size=6, chars=string.ascii_uppercase + string.digits + string.ascii_lowercase):
    random_id = ''.join(random.choice(chars) for _ in range(size))
    if not Order.objects.filter(txn_id=random_id).exists():
        return random_id
    return txn_id_generator()


class Order(models.Model):

    ORDER_STATUS_CHOICES = (("NP", "Payment Pending"), ("PL", "Order Placed"), ("RS", "Ready To Ship"),
                            ("SH", "Shipped"), ("CN", "Cancelled"))

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    items = models.ManyToManyField("carts_app.CartItem", blank=True)
    shipping_charges = models.DecimalField(max_digits=7, decimal_places=2, default=100.00)
    other_charges = models.DecimalField(max_digits=7, decimal_places=2, default=0.00)
    sub_total = models.DecimalField(max_digits=7, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=7, decimal_places=2, default=0.00)
    txn_id = models.CharField(verbose_name="Order Id", max_length=32, default=txn_id_generator, unique=True)
    delivery_expected = models.DateField(blank=True, null=True)
    bill = models.FileField(upload_to="orders/bills/", blank=True, null=True,
                            validators=[FileExtensionValidator(allowed_extensions=['pdf', ]), ])
    user_text = models.TextField(blank=True)
    receiver_name = models.CharField(max_length=64)

    line_1 = models.CharField(max_length=264, blank=True)
    line_2 = models.CharField(max_length=264, blank=True)
    locality = models.CharField(max_length=64, blank=True)
    zip_code = models.CharField(max_length=6, blank=True)
    phone = models.CharField(max_length=13, blank=True)

    bill_sms_sent = models.BooleanField(default=False)
    placed_sms_sent = models.BooleanField(default=False)
    rs_sms_sent = models.BooleanField(verbose_name="Ready to ship sms sent", default=False)

    created_on = models.DateTimeField(auto_now_add=True)

    status = models.CharField(max_length=2, choices=ORDER_STATUS_CHOICES, default="NP")
    is_payed = models.BooleanField(default=False)

    def __str__(self):
        return "{} - {} Rupees".format(self.user.phone, self.total_amount)

    @property
    def get_address_text(self):
        return "{}, {}, {}, {}".format(self.line_1, self.line_2, self.locality, self.zip_code)

    @property
    def get_delivery_expected(self):
        if self.delivery_expected:
            return self.delivery_expected.strftime("%d %b, %Y")
        else:
            return "Expected Delivery Date will be informed soon"

    @property
    def get_absolute_url(self):
        return reverse_lazy("orders:detail", kwargs={"pk": str(self.id)})

    @property
    def get_created_date(self):
        return self.created_on.strftime("%d %b, %Y")

    @property
    def get_status(self):
        return self.get_status_display()

    @property
    def get_bill_download_link(self):
        if self.bill:
            return reverse_lazy("orders:bill_download", kwargs={"txn_id": self.txn_id})
        else:
            return ""

    @property
    def get_create_payment_url(self):
        return reverse_lazy("payments:paytm_create_payment", kwargs={'txn_id': self.txn_id})

    @property
    def get_admin_email_message(self):
        return "Order placed with amount {amount} with order id {order_id} on {date}\n\nOrder Details :-\n\n" \
               "\tOrder Id = {order_id}\n\tShipping Charges{sh_charges}\n\tSub Total = {sub_total}" \
               "\n\tTotal Ammount = {amount}\n\tDate & Time = {date}\n\nVisit Administration Panel on {url}" \
               " to check details of order.\nThank You.".format(amount=self.total_amount, order_id=self.txn_id,
                date=self.created_on, sh_charges=self.shipping_charges, sub_total=self.sub_total,
                url=str(settings.SITE_DOMAIN + '/admin/orders/order/{}/change/'.format(self.id)))

    def send_bill_sms(self):
        url = "http://2factor.in/API/V1/{}/ADDON_SERVICES/SEND/TSMS".format(settings.API_KEY_2FA)
        data = {
            "From": "ALPHAH",
            "To": str(self.user.phone),
            "TemplateName": "BILL_SMS",
            "VAR1": str(self.user.get_short_name),
            "VAR2": str(self.txn_id),
            "VAR3": str(self.total_amount),
            "VAR4": str(settings.SITE_DOMAIN) + str(self.get_bill_download_link),
            "VAR5": str(self.get_delivery_expected),
            "VAR6": str(settings.SITE_DOMAIN) + str(self.get_absolute_url),
        }
        response = requests.post(url, data=data)
        response_dict = json.loads(response.content)
        print("BILL SMS : ", response_dict)
        if response_dict['Status'] == "Success":
            self.bill_sms_sent = True
            self.save()

    def send_placed_sms(self):
        url = "http://2factor.in/API/V1/{}/ADDON_SERVICES/SEND/TSMS".format(settings.API_KEY_2FA)
        data = {
            "From": "ALPHAH",
            "To": str(self.user.phone),
            "TemplateName": "PLACED_SMS",
            "VAR1": str(self.user.get_short_name),
            "VAR2": str(self.txn_id),
            "VAR3": str(self.total_amount),
            "VAR4": str(settings.SITE_DOMAIN) + str(self.get_absolute_url),

        }
        response = requests.post(url, data=data)
        response_dict = json.loads(response.content)
        if response_dict['Status'] == "Success":
            self.placed_sms_sent = True
            self.save()

    def send_rs_sms(self):
        url = "http://2factor.in/API/V1/{}/ADDON_SERVICES/SEND/TSMS".format(settings.API_KEY_2FA)
        data = {
            "From": "ALPHAH",
            "To": str(self.user.phone),
            "TemplateName": "RS_SMS",
            "VAR1": str(self.txn_id),

        }
        response = requests.post(url, data=data)
        response_dict = json.loads(response.content)
        if response_dict['Status'] == "Success":
            self.rs_sms_sent = True
            self.save()

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.placed_sms_sent and self.status == "PL":
            self.send_placed_sms()
        if not self.bill_sms_sent and self.bill and self.delivery_expected:
            self.send_bill_sms()
        if not self.rs_sms_sent and self.status == "RS":
            self.send_rs_sms()
        return super().save()

    def send_email_to_admin(self):
        subject = "New Order placed on www.alphahub.in"
        send_mail(subject=subject, message=self.get_admin_email_message, from_email=settings.EMAIL_FROM,
                  recipient_list=[settings.ADMIN_EMAIL, ])
        return True


def assign_amount(sender, instance, action, *args, **kwargs):
    sub_total = decimal.Decimal(0.00)
    for item in instance.items.all():
        sub_total += item.amount
    if instance.sub_total != sub_total:
        instance.sub_total = sub_total
        instance.save()


def assing_total_amount(sender, created, instance, *args, **kwargs):
    if instance.sub_total != 0.00:
        total_amount = instance.sub_total + decimal.Decimal(instance.shipping_charges)
        if instance.total_amount != total_amount:
            instance.total_amount = total_amount
            instance.save()


post_save.connect(assing_total_amount, sender=Order)
m2m_changed.connect(assign_amount, sender=Order.items.through)
