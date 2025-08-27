from django.db import models
from django.contrib.auth.models import User
from apps.comics.models import Comic
from utils.define import TABLE_FAVORITE_SHOW


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comic = models.ForeignKey(Comic, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = TABLE_FAVORITE_SHOW
        unique_together = (
            "user",
            "comic",
        )

    def __str__(self):
        return f"{self.user.username} - {self.comic.name}"
