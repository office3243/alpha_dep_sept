from django.db import models
from django.db.models.signals import post_save
from django.core.mail import send_mail
from django.conf import settings


class Enquiry(models.Model):
    user = models.ForeignKey("accounts.User", blank=True, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=64, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    message = models.TextField(blank=True)

    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email or str(self.created_on)

    @property
    def get_email_message(self):
        return "Hello Admin!\nThis is enquiry email from www.alphahub.in\n\nA" \
               " {} with email {} has sent you an enquiry on {}\n\nEmail : {}\n\nMessage : {}\n\nOn : {}"\
            .format(("user ({})".format(self.user)) or "Visitor", self.email, self.created_on, self.email, self.message, self.created_on)

    class Meta:
        verbose_name_plural = "Enquiries"


def send_email_to_admin(sender, created, instance, *args, **kwargs):
    if created:
        subject = "Enquiry email from www.alphahub.in"
        send_mail(subject=subject, message=instance.get_email_message, from_email=settings.EMAIL_FROM, recipient_list=[settings.ADMIN_EMAIL, ])
        instance.save()


post_save.connect(send_email_to_admin, sender=Enquiry)
