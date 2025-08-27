# from django.contrib import admin
# from .models import Cart
# from utils.define import TABLE_CART_SHOW, ADMIN_SRC_CSS, ADMIN_SRC_JS
# from utils.helpers import format_vnd


# @admin.register(Cart)
# class CartAdmin(admin.ModelAdmin):
#     list_display = ("user", "comic", "quantity", "formatted_price", "created_at")
#     list_filter = ("created_at",)
#     search_fields = ("user__username", "comic__name")
#     date_hierarchy = "created_at"
#     readonly_fields = ("user", "comic", "quantity", "formatted_price", "created_at")
#     list_per_page = 10

#     def formatted_price(self, obj):
#         return format_vnd(obj.total_price)

#     formatted_price.short_description = "total_price"

#     def get_queryset(self, request):
#         return super().get_queryset(request).select_related("user", "comic")

#     def has_add_permission(self, request, obj=None):
#         return False

#     def has_change_permission(self, request, obj=None):
#         return False

#     class Meta:
#         verbose_name_plural = TABLE_CART_SHOW

#     class Media:
#         js = ADMIN_SRC_JS
#         css = ADMIN_SRC_CSS
