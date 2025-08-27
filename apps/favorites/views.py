from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from .models import Favorite
from apps.comics.models import Comic


@require_POST
def add_to_favorite(request, comic_id):
    if not request.user.is_authenticated:
        return JsonResponse(
            {"status": "error", "message": "Vui lòng đăng nhập để thêm vào yêu thích!"},
            status=401,
        )
    try:
        comic = get_object_or_404(Comic, id=comic_id)
        favorite, created = Favorite.objects.get_or_create(
            user=request.user, comic=comic
        )
        if created:
            return JsonResponse(
                {
                    "status": "success",
                    "message": f"Đã thêm {comic.name} vào danh sách yêu thích!",
                }
            )
        else:
            return JsonResponse(
                {
                    "status": "error",
                    "message": f"{comic.name} đã có trong danh sách yêu thích!",
                },
                status=400,
            )
    except Exception as e:
        return JsonResponse(
            {"status": "error", "message": "Đã xảy ra lỗi khi thêm vào yêu thích!"},
            status=500,
        )


@require_POST
def remove_from_favorite(request, comic_id):
    if not request.user.is_authenticated:
        return JsonResponse(
            {"status": "error", "message": "Vui lòng đăng nhập để xóa khỏi yêu thích!"},
            status=401,
        )
    try:
        comic = get_object_or_404(Comic, id=comic_id)
        favorite = Favorite.objects.filter(user=request.user, comic=comic).first()
        if favorite:
            favorite.delete()
            return JsonResponse(
                {
                    "status": "success",
                    "message": f"Đã xóa {comic.name} khỏi danh sách yêu thích!",
                }
            )
        else:
            return JsonResponse(
                {
                    "status": "error",
                    "message": f"{comic.name} không có trong danh sách yêu thích!",
                },
                status=400,
            )
    except Exception as e:
        return JsonResponse(
            {"status": "error", "message": "Đã xảy ra lỗi khi xóa khỏi yêu thích!"},
            status=500,
        )


# @require_GET
# def check_favorite_status(request, comic_id):
#     if not request.user.is_authenticated:
#         return JsonResponse({"status": "success", "is_favorite": False})
#     try:
#         comic = get_object_or_404(Comic, id=comic_id)
#         is_favorite = Favorite.objects.filter(user=request.user, comic=comic).exists()
#         return JsonResponse({"status": "success", "is_favorite": is_favorite})
#     except Exception as e:
#         return JsonResponse(
#             {"status": "error", "message": "Lỗi khi kiểm tra trạng thái yêu thích!"},
#             status=500,
#         )


@require_GET
def check_multiple_favorites(request):
    comic_ids = request.GET.getlist(
        "comic_ids"
    )  # Lấy danh sách comic_ids từ query params (ví dụ: ?comic_ids=1&comic_ids=2&comic_ids=3)
    if not comic_ids:  # Nếu không có comic_ids, trả về rỗng để tránh lỗi
        return JsonResponse({"status": "success", "favorites": {}})

    if not request.user.is_authenticated:
        return JsonResponse({"status": "success", "favorites": {}})

    try:
        # Lọc các favorite của user hiện tại trong danh sách comic_ids
        favorites = Favorite.objects.filter(
            user=request.user, comic_id__in=comic_ids
        ).values("comic_id")
        favorites_map = {
            str(f["comic_id"]): True for f in favorites
        }  # Chuyển thành dict với key là str(comic_id) để dễ match
        return JsonResponse({"status": "success", "favorites": favorites_map})
    except Exception as e:
        # Xử lý lỗi (ví dụ: lỗi database), trả về phản hồi lỗi
        return JsonResponse(
            {"status": "error", "message": "Lỗi khi kiểm tra trạng thái yêu thích!"},
            status=500,
        )


@require_GET
def total_favorites(request):
    try:
        total = 0
        if request.user.is_authenticated:
            total = Favorite.objects.filter(user=request.user).count()
        return JsonResponse({"status": "success", "total": total})
    except Exception as e:
        return JsonResponse(
            {"status": "error", "message": "Lỗi khi lấy tổng số yêu thích!"}, status=500
        )


@require_GET
def favorites_list(request):
    if not request.user.is_authenticated:
        return render(request, "favorites/favorites_list.html", {"favorites": []})
    try:
        favorites = Favorite.objects.filter(user=request.user).select_related("comic")
        return render(
            request, "favorites/favorites_list.html", {"favorites": favorites}
        )
    except Exception as e:
        return render(
            request,
            "favorites/favorites_list.html",
            {"favorites": [], "error": "Lỗi khi tải danh sách yêu thích!"},
        )
