from django.db import models
from django.contrib.auth.models import User
from apps.comics.models import Comic
from utils.define import APP_VALUE_RATING_CHOICES, TABLE_RATING_SHOW


class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comic = models.ForeignKey(Comic, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=APP_VALUE_RATING_CHOICES)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = TABLE_RATING_SHOW
        indexes = [models.Index(fields=["comic"])]
        unique_together = (
            "user",
            "comic",
        )  # Đảm bảo một người dùng chỉ đánh giá một truyện một lần

    def __str__(self):
        return f"{self.user.username} - {self.comic.name} - {self.rating} stars"
