from django.contrib import admin
from django.shortcuts import render
from django.urls import path, reverse
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth, TruncDate
from django.utils.html import format_html
from .models import Order, OrderItem
from utils.helpers import format_vnd
from utils.define import (
    TABLE_ORDER_SHOW,
    TABLE_ORDER_ITEM_SHOW,
    ADMIN_SRC_CSS,
    ADMIN_SRC_JS_COMIC,
)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("comic", "formatted_price", "quantity", "formatted_total")
    fields = ("comic", "formatted_price", "quantity", "formatted_total")
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

    def formatted_price(self, obj):
        return format_vnd(obj.price)

    def formatted_total(self, obj):
        return format_vnd(obj.total)

    formatted_price.short_description = "price"
    formatted_total.short_description = "total"

    class Meta:
        verbose_name_plural = TABLE_ORDER_ITEM_SHOW


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "formatted_total",
        "payment_method",
        "created_at",
        "status",
        "payment_status",
    )
    list_filter = ("status", "payment_status", "payment_method", "created_at")
    search_fields = ("user__username",)
    readonly_fields = (
        "id",
        "user",
        "formatted_total",
        "payment_method",
        "created_at",
    )
    inlines = [OrderItemInline]
    fields = readonly_fields + (
        "status",
        "payment_status",
    )
    list_editable = (
        "status",
        "payment_status",
    )
    date_hierarchy = "created_at"
    list_per_page = 10

    def formatted_total(self, obj):
        return format_vnd(obj.total_price)

    formatted_total.short_description = "total_price"

    def has_add_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user")

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "stats/",
                self.admin_site.admin_view(self.stats_view),
                name="order-stats",
            ),
            path(
                "order-status-stats/",
                self.admin_site.admin_view(self.order_status_stats_view),
                name="order-status-stats",
            ),
        ]
        return custom_urls + urls

    def stats_view(self, request):
        selected_year = request.GET.get("year")
        selected_month = request.GET.get("month")

        # Chuyển đổi sang số nguyên với kiểm tra an toàn
        selected_year = (
            int(selected_year) if selected_year and selected_year.isdigit() else None
        )
        selected_month = (
            int(selected_month) if selected_month and selected_month.isdigit() else None
        )

        revenue_data = Order.objects.filter(payment_status="paid")

        revenue_by_month = (
            revenue_data.annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(total=Sum("total_price"))
            .order_by("month")
        )
        if selected_year:
            revenue_by_month = revenue_by_month.filter(month__year=selected_year)
        if selected_month:
            revenue_by_month = revenue_by_month.filter(month__month=selected_month)

        revenue_by_day = (
            revenue_data.annotate(day=TruncDate("created_at"))
            .values("day")
            .annotate(total=Sum("total_price"))
            .order_by("day")
        )
        if selected_month:
            revenue_by_day = revenue_by_day.filter(day__month=selected_month)
        if selected_year:
            revenue_by_day = revenue_by_day.filter(day__year=selected_year)

        years = [d.year for d in Order.objects.dates("created_at", "year")]
        months = [d.month for d in Order.objects.dates("created_at", "month")]

        context = {
            "revenue_by_month": revenue_by_month,
            "revenue_by_day": revenue_by_day,
            "years": sorted(set(years)),
            "months": sorted(set(months)),
            "selected_year": selected_year,
            "selected_month": selected_month,
        }
        return render(request, "admin/orders_stats.html", context)

    def order_status_stats_view(self, request):
        selected_year = request.GET.get("year")
        selected_month = request.GET.get("month")

        # Chuyển đổi sang số nguyên với kiểm tra an toàn
        selected_year = (
            int(selected_year) if selected_year and selected_year.isdigit() else None
        )
        selected_month = (
            int(selected_month) if selected_month and selected_month.isdigit() else None
        )

        # Thống kê theo trạng thái thanh toán
        payment_status_counts = (
            Order.objects.values("payment_status")
            .annotate(count=Count("id"))
            .order_by("payment_status")
        )
        if selected_year:
            payment_status_counts = payment_status_counts.filter(
                created_at__year=selected_year
            )
        if selected_month:
            payment_status_counts = payment_status_counts.filter(
                created_at__month=selected_month
            )

        # Thống kê theo trạng thái đơn hàng
        order_status_counts = (
            Order.objects.values("status")
            .annotate(count=Count("id"))
            .order_by("status")
        )
        if selected_year:
            order_status_counts = order_status_counts.filter(
                created_at__year=selected_year
            )
        if selected_month:
            order_status_counts = order_status_counts.filter(
                created_at__month=selected_month
            )

        # Lấy danh sách năm và tháng để tạo option
        years = [d.year for d in Order.objects.dates("created_at", "year")]
        months = [d.month for d in Order.objects.dates("created_at", "month")]

        context = {
            "payment_status_counts": payment_status_counts,
            "order_status_counts": order_status_counts,
            "years": sorted(set(years)),
            "months": sorted(set(months)),
            "selected_year": selected_year,
            "selected_month": selected_month,
        }
        return render(request, "admin/order_status_stats.html", context)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["stats_link"] = format_html(
            '<a href="{}" class="button" style="margin-bottom: 10px; display: inline-block;'
            ' padding: 8px 16px;">View revenue statistics</a>',
            reverse("admin:order-stats"),
        )
        extra_context["status_stats_link"] = format_html(
            '<a href="{}" class="button" style="margin-bottom: 10px; display: inline-block; '
            'margin-left: 10px; padding: 8px 16px;">View order status statistics</a>',
            reverse("admin:order-status-stats"),
        )
        return super().changelist_view(request, extra_context)

    class Meta:
        verbose_name_plural = TABLE_ORDER_SHOW

    class Media:
        js = ADMIN_SRC_JS_COMIC
        css = ADMIN_SRC_CSS
