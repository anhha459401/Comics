from django.db import models
from django.contrib.auth.models import User
from utils.custom_field import CustomBooleanField
from utils.define import TABLE_CATEGORY_SHOW, TABLE_COMIC_SHOW, TABLE_VIEW_HISTORY_SHOW
from utils.helpers import get_file_path, get_file_path_intro
from django.core.validators import MinValueValidator
from datetime import datetime, timedelta


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = CustomBooleanField()

    class Meta:
        verbose_name_plural = TABLE_CATEGORY_SHOW

    def __str__(self):
        return self.name


class Comic(models.Model):
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="products"
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    cover_image = models.ImageField(upload_to=get_file_path, null=True)
    intro_image_1 = models.ImageField(
        upload_to=get_file_path_intro, null=True, blank=True
    )
    intro_image_2 = models.ImageField(
        upload_to=get_file_path_intro, null=True, blank=True
    )
    intro_image_3 = models.ImageField(
        upload_to=get_file_path_intro, null=True, blank=True
    )
    author = models.CharField(max_length=100)
    price = models.DecimalField(
        max_digits=10, decimal_places=0, validators=[MinValueValidator(0)]
    )
    sale = models.PositiveIntegerField(default=0)
    stock = models.PositiveIntegerField(default=0)
    publisher = models.CharField(max_length=100, blank=True)
    published_date = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = CustomBooleanField()

    class Meta:
        verbose_name_plural = TABLE_COMIC_SHOW

    def __str__(self):
        return self.name

    @property
    def discounted_price(self):
        if self.sale > 0:
            discount = self.price * self.sale / 100
            return self.price - discount
        return self.price

    @property
    def is_new(self):
        if self.created_at:
            return self.created_at >= datetime.now(
                tz=self.created_at.tzinfo
            ) - timedelta(days=30)
        return False

    def average_rating(self):
        ratings = self.rating_set.aggregate(models.Avg("rating"))["rating__avg"]
        return round(ratings, 1) if ratings else 0


class ViewHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comic = models.ForeignKey(Comic, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = TABLE_VIEW_HISTORY_SHOW
        unique_together = ("user", "comic")

    def __str__(self):
        return f"{self.user.username} viewed {self.comic.name}"
