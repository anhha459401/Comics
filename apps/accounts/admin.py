from django.contrib import admin
from django.contrib.auth.models import Group, User
from django.contrib.auth.admin import UserAdmin
from .models import UserProfile
from utils.define import (
    TABLE_USER_PROFILE_SHOW,
    ADMIN_SRC_JS_COMIC,
    ADMIN_SRC_CSS,
)

# Gỡ đăng ký mặc định
admin.site.unregister(Group)
admin.site.unregister(User)


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    extra = 0
    fields = (
        "date_of_birth",
        "gender",
        "phone_number",
        "address",
        "created_at",
    )
    readonly_fields = (
        "date_of_birth",
        "gender",
        "phone_number",
        "address",
        "created_at",
    )
    verbose_name_plural = TABLE_USER_PROFILE_SHOW

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class CustomUserAdmin(UserAdmin):
    inlines = [UserProfileInline]
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_active",
        "date_joined",
    )
    search_fields = ("username", "email")
    list_filter = ("is_active", "date_joined")
    date_hierarchy = "date_joined"
    list_per_page = 10
    readonly_fields = (
        "username",
        "email",
        "first_name",
        "last_name",
        "last_login",
        "date_joined",
    )
    fieldsets = (
        (None, {"fields": ("username",)}),
        (
            "Personal info",
            {"fields": ("first_name", "last_name", "email", "is_active")},
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.exclude(is_superuser=True)

    def has_add_permission(self, request, obj=None):
        return False

    class Media:
        js = ADMIN_SRC_JS_COMIC
        css = ADMIN_SRC_CSS


admin.site.register(User, CustomUserAdmin)
