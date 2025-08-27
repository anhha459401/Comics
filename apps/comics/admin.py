from pyexpat.errors import messages
from django.contrib import messages
from django import forms
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.html import format_html
from django.db.models import Count
from utils.define import (
    ADMIN_SRC_JS_COMIC,
    ADMIN_SRC_CSS_COMIC,
    TABLE_CATEGORY_SHOW,
    TABLE_COMIC_SHOW,
)
from utils.helpers import format_vnd
from .models import Category, Comic, ViewHistory
from apps.favorites.models import Favorite
from apps.ratings.models import Rating


class RatingInline(admin.TabularInline):
    model = Rating
    extra = 0
    readonly_fields = ("user", "rating", "comment", "created_at")
    can_delete = False

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False


class FavoriteInline(admin.TabularInline):
    model = Favorite
    extra = 0
    readonly_fields = ("user", "created_at")
    can_delete = False

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False


class ViewHistoryInline(admin.TabularInline):
    model = ViewHistory
    extra = 0
    readonly_fields = ("user", "created_at")
    can_delete = False

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False


# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)
    list_per_page = 10

    def delete_view(self, request, object_id, extra_context=None):
        obj = self.get_object(request, object_id)
        if obj and obj.products.exists():
            self.message_user(
                request,
                f"Cannot delete this category because it is associated with {obj.products.count()} comic(s).",
                level=messages.ERROR,
            )
            # Chặn xóa, quay về trang chi tiết thể loại
            return redirect(reverse("admin:comics_category_change", args=[object_id]))
        return super().delete_view(request, object_id, extra_context)

    class Media:
        js = ADMIN_SRC_JS_COMIC
        css = ADMIN_SRC_CSS_COMIC

    class Meta:
        verbose_name_plural = TABLE_CATEGORY_SHOW


class ComicAdminForm(forms.ModelForm):
    add_stock_quantity = forms.IntegerField(
        label="Add Stock",
        min_value=0,
        required=False,
        help_text="Enter the quantity to add to current stock.",
    )

    class Meta:
        model = Comic
        fields = "__all__"


@admin.register(Comic)
class ComicAdmin(admin.ModelAdmin):
    inlines = [RatingInline, FavoriteInline, ViewHistoryInline]
    form = ComicAdminForm
    list_display = (
        "id",
        "display_cover_image",
        "name",
        "category",
        "author",
        "publisher",
        "formatted_price",
        "formatted_discount",
        "stock",
        "is_active",
        "is_new",
        "average_rating",
        "favorite_count",
        "view_count",
        "created_at",
    )

    def formatted_price(self, obj):
        return format_vnd(obj.price)

    formatted_price.short_description = "price"

    def formatted_discount(self, obj):
        return f"{obj.sale}%"

    formatted_discount.short_description = "sale"

    def favorite_count(self, obj):
        return obj.favorite_count

    favorite_count.short_description = "favorites count"

    def view_count(self, obj):
        return obj.view_count

    view_count.short_description = "views count"

    list_filter = ("is_active", "category", "created_at")
    search_fields = ("name", "author", "publisher")
    readonly_fields = ("stock",)
    date_hierarchy = "created_at"
    list_per_page = 10

    def display_cover_image(self, obj):
        if obj.cover_image:
            return format_html(
                '<img src="{}" width="50" height="50" />', obj.cover_image.url
            )
        return "No Image"

    display_cover_image.short_description = "cover_image"

    def get_queryset(self, request):
        # Annotate favorite_count và view_count cho từng comic
        queryset = super().get_queryset(request).select_related("category")
        queryset = queryset.annotate(
            favorite_count=Count("favorite", distinct=True),
            view_count=Count("viewhistory", distinct=True),
        )
        return queryset

    def save_model(self, request, obj, form, change):
        if change:
            added_stock = form.cleaned_data.get("add_stock_quantity")
            if added_stock is not None:
                if added_stock == 0:
                    messages.warning(request, "You didn't enter any quantity to add.")
                elif added_stock > 0:
                    obj.stock += added_stock
                    messages.success(
                        request,
                        f"Successfully added {added_stock} units to stock. New stock: {obj.stock}.",
                    )
        super().save_model(request, obj, form, change)

    def delete_view(self, request, object_id, extra_context=None):
        obj = self.get_object(request, object_id)
        if obj:
            # Đếm số lượng liên kết ở mỗi bảng
            cart_count = obj.cart_set.count()
            orderitem_count = obj.orderitem_set.count()
            favorite_count = obj.favorite_set.count()
            rating_count = obj.rating_set.count()

            # Tạo danh sách thông báo lỗi
            error_messages = []
            if cart_count > 0:
                error_messages.append(f"- {cart_count} item(s) in Cart")
            if orderitem_count > 0:
                error_messages.append(f"- {orderitem_count} Order Item(s)")
            if favorite_count > 0:
                error_messages.append(f"- {favorite_count} Favorite(s)")
            if rating_count > 0:
                error_messages.append(f"- {rating_count} Rating(s)")

            if error_messages:
                full_message = (
                    "Cannot delete this comic because it is still referenced in:\n"
                    + "\n".join(error_messages)
                )
                messages.error(request, full_message)
                return redirect(reverse("admin:comics_comic_change", args=[object_id]))

        return super().delete_view(request, object_id, extra_context)

    class Media:
        js = ADMIN_SRC_JS_COMIC
        css = ADMIN_SRC_CSS_COMIC

    class Meta:
        verbose_name_plural = TABLE_COMIC_SHOW
