from django.db import models
import random
import string
import decimal


def payment_order_id_generator(size=6, chars=string.ascii_uppercase + string.digits + string.ascii_lowercase):
    random_id = ''.join(random.choice(chars) for _ in range(size))
    if not Payment.objects.filter(payment_order_id=random_id).exists():
        return random_id
    return payment_order_id_generator()


class Payment(models.Model):

    GATEWAY_CHOICES = (("PT", "Paytm"), )
    STATUS_CHOICES = (("SC", "Success"), ("FL", "Failed"))

    order = models.ForeignKey("orders.Order", on_delete=models.CASCADE)
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, blank=True, null=True)
    payment_order_id = models.CharField(max_length=64, default=payment_order_id_generator)
    txnid = models.CharField(max_length=200, blank=True)
    amount = models.DecimalField(max_digits=7, decimal_places=2)
    created_on = models.DateTimeField(auto_now_add=True)
    gateway = models.CharField(max_length=2, choices=GATEWAY_CHOICES, default="PT")
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default="IN")

    def __str__(self):
        return "{} -- {} -- {}".format(self.user.phone if self.user else "Unknown", self.amount, self.payment_order_id)
