from django.urls import path
from . import views
urlpatterns = [
    path("checkout/", views.checkout, name="checkout"),
    path("mine/", views.my_orders, name="my_orders"),
    path("success/<str:order_number>/", views.order_success, name="order_success"),
    path("<str:order_number>/", views.order_detail, name="order_detail"),
    path("<str:order_number>/cancel/", views.cancel_order, name="cancel_order"),
]
