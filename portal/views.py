from django.shortcuts import render
from django.views.generic import TemplateView, View
from products.models import Category


class HomeView(TemplateView):
    template_name = "portal/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        categories = Category.objects.all()
        context['categories'] = categories
        return context


class ContactView(TemplateView):
    template_name = "portal/contact.html"

