from django.contrib import admin
from .models import Product, Photo, Rate, Category, Specification

admin.site.register(Photo)
admin.site.register(Rate)
# admin.site.register(SpecificationName)
admin.site.register(Category)
admin.site.register(Specification)


class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 1


class RateInline(admin.TabularInline):
    model = Rate
    extra = 1


class SpecificationInline(admin.TabularInline):
    model = Specification
    extra = 1


class ProductAdmin(admin.ModelAdmin):
    inlines = [PhotoInline, RateInline, SpecificationInline]
    exclude = ("slug", )
    readonly_fields = ("created_on", "updated_on")


admin.site.register(Product, ProductAdmin)
