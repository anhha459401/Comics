from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Rating
from apps.comics.models import Comic
from apps.orders.models import Order, OrderItem
from django.core.paginator import Paginator


@login_required
def add_rating(request, comic_id):
    if request.method == "POST":
        comic = get_object_or_404(Comic, id=comic_id)

        purchased = OrderItem.objects.filter(
            order__user=request.user, order__status="delivered", comic=comic
        ).exists()

        if not purchased:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Bạn chỉ có thể đánh giá truyện đã mua và đơn hàng đã hoàn tất!",
                },
                status=403,
            )

        rating = request.POST.get("rating")
        comment = request.POST.get("review", "").strip()

        if not rating or not (1 <= int(rating) <= 5):
            return JsonResponse(
                {"status": "error", "message": "Vui lòng chọn số sao hợp lệ (1-5)!"},
                status=400,
            )

        try:
            rating_obj, created = Rating.objects.update_or_create(
                user=request.user,
                comic=comic,
                defaults={"rating": rating, "comment": comment},
            )
            message = (
                "Đánh giá đã được cập nhật!" if not created else "Đánh giá đã được lưu!"
            )
            average_rating = comic.average_rating()
            total_reviews = comic.rating_set.count()
            return JsonResponse(
                {
                    "status": "success",
                    "message": message,
                    "average_rating": average_rating,
                    "total_reviews": total_reviews,
                    "has_review": True,  # Báo hiệu đã có đánh giá
                    "rating": rating_obj.rating,
                    "comment": rating_obj.comment,
                }
            )
        except Exception as e:
            return JsonResponse(
                {
                    "status": "error",
                    "message": f"Đã xảy ra lỗi khi lưu đánh giá: {str(e)}",
                },
                status=500,
            )
    return JsonResponse(
        {"status": "error", "message": "Phương thức không hợp lệ!"}, status=405
    )


def get_reviews(request, comic_id):
    comic = get_object_or_404(Comic, id=comic_id)
    page_number = request.GET.get("page", 1)
    reviews = Rating.objects.filter(comic=comic).order_by("-created_at")
    paginator = Paginator(reviews, 3)
    page_obj = paginator.get_page(page_number)
    reviews_list = page_obj.object_list

    reviews_data = [
        {
            "username": review.user.username,
            "date": review.created_at.strftime("%d %b %Y, %I:%M %p"),
            "rating": review.rating,
            "comment": review.comment if review.comment else "Không có nhận xét",
        }
        for review in reviews_list
    ]

    return JsonResponse(
        {
            "reviews": reviews_data,
            "has_previous": page_obj.has_previous(),
            "has_next": page_obj.has_next(),
            "previous_page_number": (
                page_obj.previous_page_number() if page_obj.has_previous() else None
            ),
            "next_page_number": (
                page_obj.next_page_number() if page_obj.has_next() else None
            ),
            "total_pages": paginator.num_pages,
            "current_page": page_obj.number,
        }
    )


def get_rating_data(request, comic_id):
    comic = get_object_or_404(Comic, id=comic_id)

    # Tính phân phối sao
    rating_counts = [0] * 5
    for rating in Rating.objects.filter(comic=comic).values_list("rating", flat=True):
        rating_counts[5 - int(rating)] += 1
    total_ratings = sum(rating_counts)
    rating_percentages = [
        (count / total_ratings * 100 if total_ratings > 0 else 0)
        for count in rating_counts
    ]

    return JsonResponse(
        {
            "rating_percentages": rating_percentages,
            "rating_counts": rating_counts,
        }
    )
