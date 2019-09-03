from __future__ import unicode_literals

from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import ugettext_lazy as _
from .validators import phone_number_validator
from products.models import Category
from .managers import UserManager
from carts_app.models import Cart
from django.db.models.signals import post_save


class User(AbstractBaseUser, PermissionsMixin):
    phone = models.CharField(_('phone number'), max_length=13, validators=[phone_number_validator, ], unique=True)
    email = models.EmailField(_('email address'), blank=True, null=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    created_on = models.DateTimeField(_('created_on'), auto_now_add=True)
    is_active = models.BooleanField(_('active'), default=True)
    is_staff = models.BooleanField(_('staff'), default=False)
    is_superuser = models.BooleanField(_('superuser'), default=False)
    objects = UserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    @property
    def get_full_name(self):
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    @property
    def get_short_name(self):
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)

    @property
    def get_display_text(self):
        return self.get_full_name if self.get_full_name != " " else self.phone
    
    @property
    def get_category_visiting_cards(self):
        vs_cards = Category.objects.filter(name__icontains="visiting card")
        if vs_cards.exists():
            return vs_cards.first()
        
    @property
    def get_category_pens(self):
        pens = Category.objects.filter(name__icontains="pens")
        if pens.exists():
            return pens.first()
        return False
        
    @property
    def get_category_id_cards(self):
        id_cards = Category.objects.filter(name__icontains="id card")
        if id_cards.exists():
            return id_cards.first()


def create_cart(sender, instance, *args, **kwargs):
    if not instance.is_staff and not instance.is_superuser and not hasattr(instance, "cart"):
        Cart.objects.create(user=instance)