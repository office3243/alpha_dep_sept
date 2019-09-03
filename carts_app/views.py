from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import FormView, DetailView, View, DeleteView
from django.urls import reverse_lazy
from .models import Cart, CartItem
from django.http import Http404, HttpResponse
from .forms import CartItemAddForm
from products.models import Product
import decimal
from django.core.validators import ValidationError
from django.contrib import messages
import os

def get_request_cart(request):
    if request.user.is_authenticated:
        cart = Cart.objects.get_or_create(user=request.user)[0]
        if "cart_uuid" in request.session:
            try:
                session_cart = Cart.objects.get(uuid=request.session.get("cart_uuid"))
                # session_cart.cartitem_set.all().bulk_update(cart=cart)
                for item in session_cart.cartitem_set.all():
                    item.cart = cart
                    item.save()
                del request.session['cart_uuid']
            except Exception as e:
                pass
    else:
        if "cart_uuid" in request.session:
            try:
                cart = Cart.objects.get(uuid=request.session.get("cart_uuid"))
            except Cart.DoesNotExist:
                del request.session['cart_uuid']
                return get_request_cart(request)
        else:
            cart = Cart.objects.create()
            request.session['cart_uuid'] = str(cart.uuid)
    cart.save()
    return cart


class ItemAddView(FormView):

    success_url = reverse_lazy("portal:home")
    form_class = CartItemAddForm
    template_name = "carts_app/cart_view2.html"

    def form_valid(self, form):
        temp_form = form.save(commit=False)
        # product = get_object_or_404(Product, id=form.data.get("product_id"))
        temp_form.instance.cart = get_request_cart(self.request)
        # temp_form.instance.product = product
        temp_form.save()
        return super().form_valid(temp_form)


def item_add(request):
    if request.method == "POST":
        product = get_object_or_404(Product, id=request.POST.get("product_id"), is_active=True)
        quantity = int(request.POST['quantity'])
        cart = get_request_cart(request)
        if request.FILES:
            user_file = request.FILES['user_file']
            item = CartItem(product=product, cart=cart, quantity=quantity, user_file=user_file)
        else:
            item = CartItem(product=product, cart=cart, quantity=quantity)
        try:
            item.full_clean()
            item.save()
        except ValidationError as e:
            messages.warning(request, "Getting Issues. Please Try Again.")
        return redirect("carts_app:cart_view")
    return redirect("portal:home")


class CartView(DetailView):

    template_name = "carts_app/cart_view.html"
    model = Cart

    def get_object(self, queryset=None):
        return get_request_cart(self.request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['cart_items'] = self.get_object().cartitem_set.all().order_by("-id")
        return context


class ItemDeleteView(DeleteView):

    template_name = "carts_app/cart_view.html"
    model = Cart

    def get_object(self, queryset=None):
        return get_request_cart(self.request)

#
# def item_delete(request):
#     if request.method == "POST":
#         item = get_object_or_404(CartItem, id=request.POST["item_id"], cart=get_request_cart(request))
#         item.delete()
#         messages.success(request, "Item Deleted Successfully")
#         return redirect("carts_app:cart_view")
#     return redirect("portal:home")


def item_delete(request, item_id):
    try:
        item = get_object_or_404(CartItem, id=item_id, cart=get_request_cart(request))
        item.delete()
        messages.success(request, "Item Deleted Successfully")
        return redirect("carts_app:cart_view")
    except:
        return redirect("carts_app:cart_view")


def user_file_download(request, id):
    try:
        file_path = get_object_or_404(CartItem, id=id, cart=get_request_cart(request)).user_file.path
        if os.path.exists(file_path):
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/pdf")
                response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
                return response
        raise Http404
    except Exception as e:
        print(e)
        raise Http404
