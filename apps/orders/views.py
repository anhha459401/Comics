from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from apps.cart.models import Cart
from .models import Order, OrderItem
from apps.accounts.models import UserProfile
from django.urls import reverse
import hashlib
import hmac
import urllib.parse
import time
from django.conf import settings
from utils.define import (
    ORDER_STATUS_CHOICES,
    APP_VALUE_PAYMENT_METHOD_DEFAULT,
    APP_VALUE_STATUS_DEFAULT,
    APP_VALUE_STATUS_DEFAULT_PAYMENT,
)


@login_required
def payment(request):
    cart_items = Cart.objects.filter(user=request.user).select_related("comic")
    if not cart_items:
        messages.error(request, "Giỏ hàng của bạn đang trống!")
        return redirect("cart:cart_detail")

    total_price = sum(item.total_price for item in cart_items)
    shipping_fee = 0
    if total_price < 100000:
        shipping_fee = 40000
    elif total_price < 200000:
        shipping_fee = 30000
    elif total_price < 300000:
        shipping_fee = 20000
    elif total_price < 400000:
        shipping_fee = 10000
    else:
        shipping_fee = 0

    total_price = total_price + shipping_fee
    user_profile = request.user.profile if hasattr(request.user, "profile") else None

    if request.method == "POST":
        action = request.POST.get("action")

        # Xử lý chỉnh sửa thông tin thanh toán
        # if action == "update_profile":
        #     address = request.POST.get("address")
        #     phone_number = request.POST.get("phone_number")
        #     if address and phone_number:
        #         if user_profile:
        #             user_profile.address = address
        #             user_profile.phone_number = phone_number
        #             user_profile.save()
        #         else:
        #             UserProfile.objects.create(
        #                 user=request.user, address=address, phone_number=phone_number
        #             )
        #         messages.success(request, "Cập nhật thông tin nhận hàng thành công!")
        #     else:
        #         messages.error(request, "Vui lòng nhập đầy đủ địa chỉ và số điện thoại")
        #     return redirect("orders:payment")

        if action == "checkout":
            # 1. Lưu thông tin nhận hàng vào profile
            address = request.POST.get("address")
            phone_number = request.POST.get("phone_number")

            if not address or not phone_number:
                messages.error(request, "Vui lòng nhập đầy đủ địa chỉ và số điện thoại")
                return redirect("orders:payment")

            if user_profile:
                user_profile.address = address
                user_profile.phone_number = phone_number
                user_profile.save()
            else:
                UserProfile.objects.create(
                    user=request.user, address=address, phone_number=phone_number
                )

            # 2. Lấy phương thức thanh toán
            payment_method = request.POST.get("payment_method")
            if not payment_method in ["cod", "vnpay"]:
                messages.error(request, "Phương thức thanh toán không hợp lệ!")
                return redirect("orders:payment")

            try:
                with transaction.atomic():
                    for item in cart_items:
                        if item.quantity > item.comic.stock:
                            messages.error(
                                request,
                                f"Không đủ số lượng {item.comic.name} trong kho",
                            )
                            return redirect("cart:cart_detail")

                    order = Order.objects.create(
                        user=request.user,
                        total_price=total_price,
                        status=APP_VALUE_STATUS_DEFAULT,
                        payment_status=APP_VALUE_STATUS_DEFAULT_PAYMENT,
                        payment_method=payment_method,
                    )

                    for item in cart_items:
                        OrderItem.objects.create(
                            order=order,
                            comic=item.comic,
                            quantity=item.quantity,
                            price=item.comic.discounted_price,
                        )
                        item.comic.stock -= item.quantity
                        item.comic.save()

                    cart_items.delete()

                    if payment_method == APP_VALUE_PAYMENT_METHOD_DEFAULT:
                        messages.success(
                            request, f"Đặt hàng thành công! Mã đơn hàng: {order.id}"
                        )
                        return redirect("orders:order_detail", order_id=order.id)
                    elif payment_method == "vnpay":
                        payment_url = create_vnpay_payment(order)
                        return redirect(payment_url)

            except Exception as e:
                messages.error(request, f"Lỗi khi xử lý thanh toán: {str(e)}")
                return redirect("orders:payment")

    return render(
        request,
        "orders/payment.html",
        {
            "cart_items": cart_items,
            "total_price": total_price,
            "shipping_fee": shipping_fee,
            "user_profile": user_profile,
        },
    )


def create_vnpay_payment(order):
    vnp_url = "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html"
    vnp_tmn_code = settings.VNPAY_TMN_CODE  # Sử dụng trực tiếp từ settings
    vnp_hash_secret = settings.VNPAY_HASH_SECRET

    order_id = f"{order.id}_{int(time.time())}"
    amount = int(order.total_price * 100)  # Đảm bảo là số nguyên
    order_desc = f"Thanh toán đơn hàng #{order.id}"
    vnp_params = {
        "vnp_Version": "2.1.0",
        "vnp_Command": "pay",
        "vnp_TmnCode": vnp_tmn_code,
        "vnp_Amount": amount,
        "vnp_CurrCode": "VND",
        "vnp_TxnRef": order_id,
        "vnp_OrderInfo": order_desc,
        "vnp_OrderType": "250000",
        "vnp_Locale": "vn",
        "vnp_ReturnUrl": settings.SITE_URL + reverse("orders:payment_callback"),
        "vnp_IpAddr": "127.0.0.1",
        "vnp_CreateDate": time.strftime("%Y%m%d%H%M%S"),  # Đảm bảo định dạng
    }

    # Sắp xếp và tạo query string
    sorted_params = sorted(vnp_params.items())
    query_string = urllib.parse.urlencode(sorted_params)

    # Tạo chữ ký
    vnp_secure_hash = hmac.new(
        vnp_hash_secret.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha512
    ).hexdigest()

    vnp_params["vnp_SecureHash"] = vnp_secure_hash
    vnpay_url = f"{vnp_url}?{query_string}&vnp_SecureHash={vnp_secure_hash}"
    return vnpay_url


@login_required
def payment_callback(request):
    if request.method == "GET":
        vnp_params = request.GET.dict()
        vnp_secure_hash = vnp_params.pop("vnp_SecureHash", None)
        if not vnp_secure_hash:
            messages.error(request, "Thiếu chữ ký bảo mật!")
            return redirect("orders:orders")

        # Tạo lại query string để xác minh
        sorted_params = sorted(vnp_params.items())
        query_string = urllib.parse.urlencode(sorted_params)
        calculated_hash = hmac.new(
            settings.VNPAY_HASH_SECRET.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha512,
        ).hexdigest()

        order_id = vnp_params.get("vnp_TxnRef").split("_")[0]
        order = get_object_or_404(Order, id=order_id, user=request.user)

        if calculated_hash != vnp_secure_hash:
            messages.error(request, "Chữ ký không hợp lệ!")
            return redirect("orders:orders")

        vnp_response_code = vnp_params.get("vnp_ResponseCode")
        if vnp_response_code == "00":
            order_id = vnp_params.get("vnp_TxnRef").split("_")[0]
            order = get_object_or_404(Order, id=order_id, user=request.user)
            order.status = APP_VALUE_STATUS_DEFAULT
            order.payment_status = "paid"
            order.save()
            messages.success(request, f"Thanh toán thành công! Mã đơn hàng: {order.id}")
        else:
            order_items = OrderItem.objects.filter(order=order)
            for item in order_items:
                comic = item.comic
                comic.stock += item.quantity
                comic.save()

            order.payment_status = "failed"
            order.status = "cancelled"
            order.save()
            messages.error(request, f"Thanh toán thất bại! Mã lỗi: {vnp_response_code}")
        return redirect("orders:order_detail", order_id=order_id)


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    total_price = order.total_price
    shipping_fee = 0
    if total_price < 100000:
        shipping_fee = 40000
    elif total_price < 200000:
        shipping_fee = 30000
    elif total_price < 300000:
        shipping_fee = 20000
    elif total_price < 400000:
        shipping_fee = 10000
    else:
        shipping_fee = 0

    total_price = total_price + shipping_fee

    is_cancel = is_return = False
    if order.status in ["pending", "confirmed", "preparing"]:
        is_cancel = True

    if order.status == "delivered":
        is_return = True

    return render(
        request,
        "orders/order_detail.html",
        {
            "order": order,
            "is_cancel": is_cancel,
            "is_return": is_return,
            "shipping_fee": shipping_fee,
        },
    )


@login_required
def orders(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    status_filter = request.GET.get("status", "all")

    if status_filter != "all":
        orders = orders.filter(status=status_filter)

    limit = 5
    offset = int(request.GET.get("offset", 0))
    paginated_orders = orders[offset : offset + limit]
    has_more = len(orders) > offset + limit

    return render(
        request,
        "orders/orders.html",
        {
            "orders": paginated_orders,
            "has_more": has_more,
            "offset": offset + limit,
            "status_filter": status_filter,
            "status_choices": [item[0] for item in ORDER_STATUS_CHOICES],
            "ORDER_STATUS_CHOICES": ORDER_STATUS_CHOICES,
        },
    )


@login_required
def cancel_order(request, order_id):
    order = Order.objects.filter(id=order_id, user=request.user).first()
    if not order:
        return JsonResponse({"success": False, "message": "Không tìm thấy đơn hàng."})

    if order.status in ["pending", "confirmed", "preparing"]:
        order.status = "cancelled"
        if order.payment_status == "paid":
            order.payment_status = "refunded"
        order.save()
        return JsonResponse(
            {
                "success": True,
                "message": "Đơn hàng đã được hủy.",
                "order_status": order.get_status_display(),
                "payment_status": order.get_payment_status_display(),
            }
        )
    else:
        return JsonResponse(
            {
                "success": False,
                "message": "Không thể hủy đơn hàng ở trạng thái hiện tại.",
            }
        )


@login_required
def return_order(request, order_id):
    order = Order.objects.filter(id=order_id, user=request.user).first()
    if not order:
        return JsonResponse({"success": False, "message": "Không tìm thấy đơn hàng."})

    if order.status == "delivered":
        order.status = "returned"
        order.save()
        return JsonResponse(
            {
                "success": True,
                "message": "Yêu cầu trả hàng đã được ghi nhận.",
                "order_status": order.get_status_display(),
                "payment_status": order.get_payment_status_display(),
            }
        )
    else:
        return JsonResponse(
            {"success": False, "message": "Không thể trả hàng ở trạng thái hiện tại."}
        )
