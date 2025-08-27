from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from .models import Cart
from apps.comics.models import Comic
from django.http import JsonResponse
from django.template.loader import render_to_string


@login_required
def cart_add(request, comic_id):
    comic = get_object_or_404(Comic, id=comic_id)

    if request.method == "POST":
        quantity = int(request.POST.get("quantity", 1))
        cart_item, created = Cart.objects.get_or_create(user=request.user, comic=comic)

        if not created:
            if comic.stock >= cart_item.quantity + quantity:
                cart_item.quantity += quantity
                cart_item.save()
                return JsonResponse(
                    {
                        "status": "success",
                        "message": f"Đã thêm {quantity} truyện {comic.name} vào giỏ hàng",
                    }
                )
            else:
                return JsonResponse(
                    {
                        "status": "error",
                        "message": f"Không đủ số lượng {comic.name} trong kho",
                    },
                    status=400,
                )
        else:
            if comic.stock >= quantity:
                cart_item.quantity = quantity
                cart_item.save()
                return JsonResponse(
                    {
                        "status": "success",
                        "message": f"Đã thêm {quantity} truyện {comic.name} vào giỏ hàng",
                    }
                )
            else:
                cart_item.delete()
                return JsonResponse(
                    {
                        "status": "error",
                        "message": f"Không đủ số lượng {comic.name} trong kho",
                    },
                    status=400,
                )

    return JsonResponse(
        {
            "status": "error",
            "message": "Chỉ hỗ trợ phương thức POST",
        },
        status=405,
    )


@login_required
def cart_remove(request, comic_id):
    cart_item = get_object_or_404(Cart, user=request.user, comic_id=comic_id)
    comic_name = cart_item.comic.name
    cart_item.delete()
    return JsonResponse(
        {"status": "success", "message": f"Đã xóa {comic_name} khỏi giỏ hàng"}
    )


@login_required
def total_comics(request):
    cart_items = Cart.objects.filter(user=request.user).select_related("comic")
    total_price = sum(item.total_price for item in cart_items)
    return JsonResponse(
        {
            "status": "success",
            "total_items": cart_items.count(),
            "total_price": total_price,
        }
    )


@login_required
def cart_update(request, comic_id):
    if request.method == "POST":
        quantity = int(request.POST.get("quantity", 1))
        cart_item = get_object_or_404(Cart, user=request.user, comic_id=comic_id)

        if quantity > 0 and quantity <= cart_item.comic.stock:
            cart_item.quantity = quantity
            cart_item.save()
            return JsonResponse(
                {
                    "status": "success",
                    "message": f"Đã cập nhật số lượng cho {cart_item.comic.name}",
                }
            )
        elif quantity <= 0:
            cart_item.delete()
            return JsonResponse(
                {
                    "status": "success",
                    "message": f"Đã xóa {cart_item.comic.name} khỏi giỏ hàng",
                }
            )
        else:
            return JsonResponse(
                {
                    "status": "error",
                    "message": f"Không đủ số lượng {cart_item.comic.name} trong kho",
                },
                status=400,
            )

    return JsonResponse(
        {
            "status": "error",
            "message": "Chỉ hỗ trợ phương thức POST",
        },
        status=405,
    )


@login_required
def cart_detail(request):
    cart_items = Cart.objects.filter(user=request.user).select_related("comic")
    total_price = sum(item.total_price for item in cart_items)

    return render(
        request,
        "cart/cart_detail.html",
        {"cart_items": cart_items, "total_price": total_price},
    )


def cart_dropdown_partial(request):
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user).select_related("comic")
        total_price = sum(item.total_price for item in cart_items)
    else:
        cart_items = []
        total_price = 0
    html = render_to_string(
        "cart/cart_dropdown_partial.html",
        {"cart_items": cart_items, "total_price": total_price},
        request=request,
    )
    return JsonResponse({"status": "success", "html": html})


@login_required
def cart_detail_partial(request):
    cart_items = Cart.objects.filter(user=request.user).select_related("comic")
    total_price = sum(item.total_price for item in cart_items)
    html = render_to_string(
        "cart/cart_detail_partial.html",
        {
            "cart_items": cart_items,
            "total_price": total_price,
        },
        request=request,
    )
    return JsonResponse({"status": "success", "html": html})
