from django.shortcuts import render, redirect
from .forms import EnquiryAddForm
from django.contrib import messages


def add_enquiry(request):
    if request.method == "POST":
        form = EnquiryAddForm(request.POST)
        if form.is_valid():
            if request.user.is_authenticated:
                form = form.save(commit=False)
                form.user = request.user
            form.save()
            messages.success(request, "Your enquiry has been recieved. We will reply you within 4 hours.")
    return redirect("portal:contact")
