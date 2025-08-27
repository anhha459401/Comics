from django.urls import path
from . import views

app_name = "cart"

urlpatterns = [
    path("add/<int:comic_id>", views.cart_add, name="cart_add"),
    path("remove/<int:comic_id>", views.cart_remove, name="cart_remove"),
    path("update/<int:comic_id>", views.cart_update, name="cart_update"),
    path("detail", views.cart_detail, name="cart_detail"),
    path("total", views.total_comics, name="total_comics"),
    path("dropdown", views.cart_dropdown_partial, name="cart_dropdown_partial"),
    path("detail-partial", views.cart_detail_partial, name="cart_detail_partial"),
]
