from django.db import models
from django.contrib.auth.models import User
from utils.define import TABLE_USER_PROFILE_SHOW, TABLE_PASSWORD_RESET_TOKEN_SHOW
from django.utils import timezone
import uuid
from datetime import date

# Create your models here.


class UserProfile(models.Model):

    GENDER_CHOICES = (("male", "Nam"), ("female", "Nữ"), ("other", "Khác"))

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    date_of_birth = models.DateField(null=True, blank=False)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default="male")
    address = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = TABLE_USER_PROFILE_SHOW

    def __str__(self):
        return f"{self.user.username}'s profile"

    @property
    def age(self):
        if self.date_of_birth:
            today = date.today()
            age = (
                today.year
                - self.date_of_birth.year
                - (
                    (today.month, today.day)
                    < (self.date_of_birth.month, self.date_of_birth.day)
                )
            )
            return age
        return None


class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        verbose_name_plural = TABLE_PASSWORD_RESET_TOKEN_SHOW

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(hours=1)
        super().save(*args, **kwargs)

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"Password reset token for {self.user.username}"
