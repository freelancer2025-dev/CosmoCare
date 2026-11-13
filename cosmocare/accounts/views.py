from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import RegisterForm, AddressForm

def register(request):
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Welcome to CosmoCare.")
        return redirect("home")
    return render(request, "accounts/register.html", {"form": form})

@login_required
def profile(request):
    addresses = request.user.addresses.all()
    form = AddressForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        address = form.save(commit=False)
        address.user = request.user
        address.is_default = not addresses.exists()
        address.save()
        messages.success(request, "Address saved.")
        return redirect("profile")
    return render(request, "accounts/profile.html", {"addresses": addresses, "form": form})
