from django.shortcuts import render, get_object_or_404, redirect
from carts_app.views import get_request_cart
from .models import Order
from django.views.generic import DetailView, ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from .forms import OrderPlaceForm
import os
from django.conf import settings
from django.http import HttpResponse, Http404


@login_required
def place(request):
    if request.method == "POST":
        form = OrderPlaceForm(request.POST)
        if form.is_valid():
            cart = get_request_cart(request)
            line_1, line_2, locality, zip_code, phone = request.POST['line_1'], request.POST['line_2'], request.POST['locality'], request.POST['zip_code'], request.POST['phone']
            order = Order.objects.create(user=request.user, line_1=line_1, line_2=line_2, locality=locality, zip_code=zip_code, phone=phone)
            for item in cart.cartitem_set.all():
                order.items.add(item)
                item.cart = None
                item.save()
            order.save()
            print(order.items.all())
            return redirect(order.get_create_payment_url)
    return redirect("carts_app:cart_view")


class OrderPlaceView(LoginRequiredMixin, CreateView):
    model = Order
    fields = ("line_1", "line_2", "locality", "zip_code", "phone")
    success_url = "/"

    def form_valid(self, form):
        form = form.save(commit=False)
        form.instance.user = self.request.user
        super().form_valid(form)


class OrderDetailView(LoginRequiredMixin, DetailView):

    model = Order
    template_name = "orders/detail.html"
    slug_url_kwarg = "pk"
    slug_field = "pk"

    def get_object(self, queryset=None):
        order = super().get_object()
        order.save()
        if order.user == self.request.user:
            return order
        else:
            raise Http404("Not matching Order")


class OrderListView(LoginRequiredMixin, ListView):

    model = Order
    template_name = "orders/list.html"
    context_object_name = "orders"
    ordering = "-created_on"

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset()
        return qs.filter(user=self.request.user)


def bill_download(request, txn_id):
    try:
        file_path = get_object_or_404(Order, txn_id=txn_id, user=request.user).bill.path
        if os.path.exists(file_path):
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/pdf")
                response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
                return response
        raise Http404
    except Exception as e:
        print(e)
        raise Http404
