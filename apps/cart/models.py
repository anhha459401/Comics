from django.db import models
from django.contrib.auth.models import User
from apps.comics.models import Comic
from utils.define import TABLE_CART_SHOW


# Create your models here.
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comic = models.ForeignKey(Comic, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = TABLE_CART_SHOW
        unique_together = ("user", "comic")

    def __str__(self):
        return f"{self.user.username} - {self.comic.name} x {self.quantity}"

    @property
    def total_price(self):
        if self.comic is None or self.quantity is None:
            return 0
        return self.quantity * self.comic.discounted_price
