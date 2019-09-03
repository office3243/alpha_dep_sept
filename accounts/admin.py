from django.contrib import admin
from .models import User

admin.site.site_header = "Alphahub Administration"
admin.site.site_title = "Alphahub Administration"

admin.site.register(User)
