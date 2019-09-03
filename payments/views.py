from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.conf import settings
from . import paytm_checksum as Checksum
from django.http import Http404
import decimal
from django.contrib import messages
from django.contrib.auth import login
from .models import Payment
from . import alert_messages
from orders.models import Order


def create_payment(request, txn_id):
    MERCHANT_KEY = settings.PAYTM_MERCHANT_KEY
    MERCHANT_ID = settings.PAYTM_MERCHANT_ID
    CALLBACK_URL = settings.PAYTM_CALLBACK_URL
    user = request.user
    order = get_object_or_404(Order, txn_id=txn_id, user=user)
    if not order.is_payed:
        payment = Payment.objects.create(user=user, order=order, amount=order.total_amount)

        data_dict = {
                    'MID': MERCHANT_ID,
                    'ORDER_ID': payment.payment_order_id,
                    'TXN_AMOUNT': order.total_amount,
                    'CUST_ID': str(user.id),
                    'INDUSTRY_TYPE_ID':'Retail',
                    'WEBSITE': settings.PAYTM_WEBSITE,
                    'CHANNEL_ID':'WEB',
                    'CALLBACK_URL':CALLBACK_URL,
                }
        param_dict = data_dict
        param_dict['CHECKSUMHASH'] = Checksum.generate_checksum(data_dict, MERCHANT_KEY)
        return render(request, "payments/paytm/payment.html", {'paytmdict':param_dict})
    else:
        messages.warning(request, "Order already placed!")
        return redirect(order.get_absolute_url)

#
# @csrf_exempt
# def response(request):
#     if request.method == "POST":
#         MERCHANT_KEY = settings.PAYTM_MERCHANT_KEY
#         data_dict = {}
#         for key in request.POST:
#             data_dict[key] = request.POST[key]
#         verify = Checksum.verify_checksum(data_dict, MERCHANT_KEY, data_dict['CHECKSUMHASH'])
#         if verify:
#             pt_status = data_dict.get("STATUS")
#             status = "SC" if pt_status == "TXN_SUCCESS" else "FL"
#             order_id = data_dict.get("ORDERID")
#             amount = float(data_dict.get("TXNAMOUNT"))
#             txnid = data_dict.get("TXNID")
#             payment = Payment.objects.create(payment_order_id=order_id, amount=amount, user=request.user, status=status,
#                                              txnid=txnid)
#             orders = Order.objects.filter(txn_id=order_id, amount=amount, user=request.user)
#             if orders.exists():
#                 order = orders.first()
#                 if status == "TXN_SUCCESS":
#                     payment.order = order
#                     payment.save()
#                     order.is_payed = True
#                     order.save()
#                     messages.success(request, alert_messages.ORDER_PLACED_MESSAGE)
#                     return redirect(order.get_absolute_url)
#                 else:
#                     messages.warning(request, "Payment Failed. Try again.")
#                     return redirect(order.get_absolute_url)
#             else:
#                 messages.warning(request, "Payment Successfull but Order not Found. Amount will be refunded")
#
#             return redirect("orders:list")
#         else:
#             return Http404("Payment not verified")
#     return Http404("Bad Request")


@csrf_exempt
def response(request):
    if request.method == "POST":
        MERCHANT_KEY = settings.PAYTM_MERCHANT_KEY
        data_dict = {}
        for key in request.POST:
            data_dict[key] = request.POST[key]
        verify = Checksum.verify_checksum(data_dict, MERCHANT_KEY, data_dict['CHECKSUMHASH'])
        if verify:
            pt_status = data_dict.get("STATUS")
            payment_order_id = data_dict.get("ORDERID")
            amount = float(data_dict.get("TXNAMOUNT"))
            txnid = data_dict.get("TXNID")
            try:
                payment = Payment.objects.get(payment_order_id=payment_order_id, amount=amount)
                user = payment.user
                login(request, user)
                order = payment.order
                if pt_status == "TXN_SUCCESS":
                    payment.status = "SC"
                    payment.txnid = txnid
                    payment.save()
                    order.is_payed = True
                    order.status = "PL"
                    order.save()
                    order.send_email_to_admin()
                    messages.success(request, alert_messages.ORDER_PLACED_MESSAGE)
                    return redirect(order.get_absolute_url)
                else:
                    payment.status = "FL"
                    payment.txnid = txnid
                    payment.save()
                    messages.warning(request, alert_messages.PAYMENT_FAILED)
                    return redirect(order.get_absolute_url)
            except Payment.DoesNotExist:
                messages.warning(request, alert_messages.PAYMENT_NOT_FOUND)
                return redirect("orders:list")
        else:
            return Http404("Payment not verified")
    return Http404("Bad Request")
