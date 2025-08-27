from django.urls import path
from . import views
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render

app_name = "orders"

urlpatterns = [
    path("payment/", views.payment, name="payment"),
    path("order/<int:order_id>/", views.order_detail, name="order_detail"),
    path("payment/callback/", views.payment_callback, name="payment_callback"),
    path("", views.orders, name="orders"),
    path("cancel/<int:order_id>", views.cancel_order, name="cancel_order"),
    path("return/<int:order_id>", views.return_order, name="return_order"),
]
