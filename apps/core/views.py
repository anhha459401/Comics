from django.shortcuts import render
from apps.comics.models import Comic, ViewHistory
from apps.favorites.models import Favorite
from apps.cart.models import Cart
from apps.recommendations.content_based import get_content_based_recommendations
from apps.recommendations.collaborative import (
    get_collaborative_recommendations,
    train_collaborative_filtering,
)
import time


# Create your views here.
def index(request):

    # Tính năng AI
    recommended_comics = Comic.objects.filter(is_active=True).order_by("-created_at")[
        :10
    ]

    if request.user.is_authenticated:

        user = request.user
        start_time = time.time()
        print("[AI] Training collaborative filtering model...")
        model = train_collaborative_filtering(user_id=user.id)
        elapsed_time = time.time() - start_time

        if model:
            print(f"[AI] Model trained successfully in {elapsed_time:.2f} seconds.")
            cf_result = get_collaborative_recommendations(user.id, model)
        else:
            # print("[AI] No data available to train model.")
            cf_result = Comic.objects.none()  # không có kết quả CF

        # Nếu collaborative không trả về kết quả → fallback Content-Based
        if not cf_result.exists():
            last_cart = Cart.objects.filter(user=user).order_by("-created_at").first()
            if last_cart:
                print(
                    f"[AI] Fallback Content-Based: CART -> comic_id={last_cart.comic.id}"
                )
                recommended_comics = get_content_based_recommendations(
                    user.id, last_cart.comic.id
                )
            else:
                last_favorite = (
                    Favorite.objects.filter(user=user).order_by("-created_at").first()
                )
                if last_favorite:
                    print(
                        f"[AI] Fallback Content-Based: FAVORITE -> comic_id={last_favorite.comic.id}"
                    )
                    recommended_comics = get_content_based_recommendations(
                        user.id, last_favorite.comic.id
                    )
                else:
                    last_view = (
                        ViewHistory.objects.filter(user=user)
                        .order_by("-created_at")
                        .first()
                    )
                    if last_view:
                        print(
                            f"[AI] Fallback Content-Based: VIEW -> comic_id={last_view.comic.id}"
                        )
                        recommended_comics = get_content_based_recommendations(
                            user.id, last_view.comic.id
                        )
        else:
            recommended_comics = cf_result

    # Lấy 10 sản phẩm có sale lớn nhất (sale > 0) và còn hàng
    top_sale_comics = Comic.objects.filter(
        sale__gt=0, stock__gt=0, is_active=True
    ).order_by("-sale")[:10]

    # Nếu không có sản phẩm đang sale, lấy 10 sản phẩm giá thấp nhất
    if not top_sale_comics.exists():
        top_sale_comics = Comic.objects.filter(stock__gt=0, is_active=True).order_by(
            "price"
        )[:10]

    return render(
        request,
        "index.html",
        {
            "comics": recommended_comics,
            "top_sale_comics": top_sale_comics,
        },
    )
