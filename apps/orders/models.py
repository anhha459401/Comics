from django.db import models
from django.contrib.auth.models import User
from utils.define import (
    ORDER_STATUS_CHOICES,
    PAYMENT_METHOD_CHOICES,
    TABLE_ORDER_SHOW,
    TABLE_ORDER_ITEM_SHOW,
    APP_VALUE_STATUS_DEFAULT,
    APP_VALUE_PAYMENT_METHOD_DEFAULT,
    PAYMENT_STATUS_CHOICES,
    APP_VALUE_STATUS_DEFAULT_PAYMENT,
)


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20, choices=ORDER_STATUS_CHOICES, default=APP_VALUE_STATUS_DEFAULT
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default=APP_VALUE_STATUS_DEFAULT_PAYMENT,
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default=APP_VALUE_PAYMENT_METHOD_DEFAULT,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = TABLE_ORDER_SHOW

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    comic = models.ForeignKey("comics.Comic", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name_plural = TABLE_ORDER_ITEM_SHOW

    @property
    def total(self):
        if self.price is None or self.quantity is None:
            return 0
        return self.price * self.quantity

    def __str__(self):
        return f"{self.comic.name} x {self.quantity}"
