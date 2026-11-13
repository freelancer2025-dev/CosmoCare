from django.urls import path
from . import views
urlpatterns = [
    path("checkout/<str:order_number>/", views.payment_checkout, name="payment_checkout"),
    path("verify/<str:order_number>/", views.verify_payment, name="verify_payment"),
    path("razorpay/webhook/", views.razorpay_webhook, name="razorpay_webhook"),
]
