from django.shortcuts import render, get_object_or_404
from .models import Comic, Category, ViewHistory
from apps.orders.models import OrderItem
from apps.ratings.models import Rating
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import Http404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required


def comic_list(request):
    # Lấy tham số sắp xếp từ query string, mặc định là 'name_asc'
    sort = request.GET.get("sort", "name_asc")
    comics = Comic.objects.filter(is_active=True)

    # Xử lý sắp xếp
    if sort == "name_desc":
        comics = comics.order_by("-name")
    elif sort == "price_asc":
        comics = comics.order_by("price")
    elif sort == "price_desc":
        comics = comics.order_by("-price")
    elif sort == "date_asc":
        comics = comics.order_by("created_at")
    elif sort == "date_desc":
        comics = comics.order_by("-created_at")
    else:
        comics = comics.order_by("name")  # Mặc định: name_asc

    # Lấy danh sách các thể loại từ query string (hỗ trợ nhiều thể loại)
    category_slugs = request.GET.getlist("category")
    if category_slugs:
        comics = comics.filter(category__slug__in=category_slugs).distinct()

    # Phân trang
    products_per_page = 6
    paginator = Paginator(comics, products_per_page)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Tính toán thông tin hiển thị
    start_index = page_obj.start_index()
    end_index = page_obj.end_index()
    total_products = paginator.count

    # Chỉ hiển thị display_range nếu có ít nhất một truyện
    display_range = ""
    if total_products > 0:
        if start_index == end_index:
            display_range = f"Hiển thị 1 truyện trong tổng số {total_products} truyện"
        else:
            display_range = f"Hiển thị {start_index} - {min(end_index, total_products)} truyện trong tổng số {total_products} truyện"

    # Lấy danh sách thể loại và số lượng truyện active
    categories = Category.objects.filter(is_active=True).annotate(
        active_comic_count=Count("products", filter=Q(products__is_active=True))
    )

    return render(
        request,
        "comics/comic_list.html",
        {
            "page_obj": page_obj,
            "display_range": display_range,
            "total_pages": paginator.num_pages,
            "categories": categories,
            "sort": sort,
            "category_slugs": category_slugs,  # Truyền danh sách slugs để đánh dấu các checkbox đã chọn
        },
    )


# @login_required
# def track_view(request):
#     if request.method == "POST":
#         comic_slug = request.POST.get("comic_slug")
#         comic = get_object_or_404(Comic, slug=comic_slug, is_active=True)
#         ViewHistory.objects.get_or_create(user=request.user, comic=comic)
#         return JsonResponse({"status": "success"})
#     return JsonResponse({"status": "error"}, status=400)


def comic_detail(request, slug):
    comic = get_object_or_404(Comic, slug=slug, is_active=True)
    # Lấy 4 truyện liên quan cùng thể loại, loại trừ truyện hiện tại, sắp xếp ngẫu nhiên
    related_comics = (
        Comic.objects.filter(category=comic.category, is_active=True)
        .exclude(slug=slug)
        .order_by("?")[:4]
    )

    # Kiểm tra quyền đánh giá
    purchased = False
    rating_obj = None
    if request.user.is_authenticated:
        # Ghi lại lịch sử xem nếu người dùng đã đăng nhập
        ViewHistory.objects.get_or_create(user=request.user, comic=comic)

        purchased = OrderItem.objects.filter(
            order__user=request.user, order__status="delivered", comic=comic
        ).exists()
        # Lấy đánh giá hiện tại của người dùng (nếu có)
        if purchased:
            rating_obj = Rating.objects.filter(user=request.user, comic=comic).first()

    # Tính trung bình và số lượng đánh giá
    average_rating = comic.average_rating()  # Giả định phương thức này tồn tại
    total_reviews = comic.rating_set.count()

    # Lấy danh sách đánh giá với phân trang
    reviews = Rating.objects.filter(comic=comic).order_by("-created_at")
    paginator = Paginator(reviews, 3)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)
    reviews_list = page_obj.object_list

    # Tính phân phối sao
    rating_counts = [0] * 5
    for rating in Rating.objects.filter(comic=comic).values_list("rating", flat=True):
        rating_counts[5 - int(rating)] += 1
    total_ratings = sum(rating_counts)
    rating_percentages = [
        (count / total_ratings * 100 if total_ratings > 0 else 0)
        for count in rating_counts
    ]

    # Tính số lượt xem
    view_count = comic.viewhistory_set.count()

    context = {
        "comic": comic,
        "related_comics": related_comics,
        "average_rating": average_rating,
        "total_reviews": total_reviews,
        "reviews": reviews_list,
        "purchased": purchased,
        "page_obj": page_obj,
        "rating_percentages": rating_percentages,
        "rating_counts": rating_counts,
        "rating_obj": rating_obj,
        "view_count": view_count,
    }
    return render(request, "comics/comic_detail.html", context)


# Định nghĩa ánh xạ sắp xếp
SORT_MAPPING = {
    "name_asc": "name",
    "name_desc": "-name",
    "price_asc": "price",
    "price_desc": "-price",
    "date_asc": "created_at",
    "date_desc": "-created_at",
}


def search_comics(request):
    query = request.GET.get("q", "")
    sort = request.GET.get("sort", "name_asc")  # Mặc định sắp xếp theo tên A-Z

    comics = Comic.objects.all()
    if query:
        comics = comics.filter(
            Q(name__icontains=query)
            | Q(author__icontains=query)
            | Q(category__name__icontains=query)
        ).distinct()

    comics = comics.order_by(SORT_MAPPING.get(sort, "name"))

    # Phân trang
    paginator = Paginator(comics, 8)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Tính range hiển thị
    start_index = (page_obj.number - 1) * paginator.per_page + 1
    end_index = min(page_obj.number * paginator.per_page, comics.count())
    display_range = ""
    if comics.count() > 0:
        display_range = (
            f"Hiển thị {start_index} - {end_index} trong {comics.count()} sản phẩm"
        )

    return render(
        request,
        "comics/search_results.html",
        {
            "comics": page_obj,
            "page_obj": page_obj,
            "query": query,
            "sort": sort,
            "display_range": display_range,
            "total_pages": paginator.num_pages,
        },
    )


@login_required
def view_history(request):
    # Lấy danh sách lịch sử xem của người dùng hiện tại
    view_histories = (
        ViewHistory.objects.filter(user=request.user)
        .select_related("comic")
        .order_by("-created_at")
    )

    # Xử lý sắp xếp
    sort = request.GET.get("sort", "date_desc")  # Mặc định sắp xếp theo ngày mới nhất
    if sort == "name_asc":
        view_histories = view_histories.order_by("comic__name")
    elif sort == "name_desc":
        view_histories = view_histories.order_by("-comic__name")
    elif sort == "price_asc":
        view_histories = view_histories.order_by("comic__price")
    elif sort == "price_desc":
        view_histories = view_histories.order_by("-comic__price")
    elif sort == "date_asc":
        view_histories = view_histories.order_by("created_at")
    else:  # date_desc
        view_histories = view_histories.order_by("-created_at")

    # Phân trang
    paginator = Paginator(view_histories, 8)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    # Tính toán phạm vi hiển thị
    total_items = paginator.count
    start_index = (page_obj.number - 1) * paginator.per_page + 1
    end_index = min(start_index + paginator.per_page - 1, total_items)
    display_range = ""
    if view_histories.count() > 0:
        display_range = f"Hiển thị {start_index} - {end_index} trong {view_histories.count()} sản phẩm"
    # display_range = f"Hiển thị {start_index}-{end_index} của {total_items} truyện"

    context = {
        "page_obj": page_obj,
        "sort": sort,
        "display_range": display_range,
        "total_pages": paginator.num_pages,
    }
    return render(request, "comics/view_history.html", context)


def comic_categories_by_slug(request, slug):
    # Kiểm tra slug hợp lệ
    if not Category.objects.filter(slug=slug, is_active=True).exists():
        raise Http404("Danh mục không tồn tại")

    # Lấy tham số sắp xếp
    sort = request.GET.get("sort", "name_asc")
    sort_field = SORT_MAPPING.get(sort, "name")

    # Lấy danh sách truyện theo slug và sắp xếp
    comics = (
        Comic.objects.filter(is_active=True, category__slug=slug)
        .select_related("category")
        .order_by(sort_field)
    )

    # Phân trang
    products_per_page = 6
    paginator = Paginator(comics, products_per_page)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Tính toán thông tin hiển thị
    start_index = page_obj.start_index()
    end_index = page_obj.end_index()
    total_products = paginator.count
    display_range = (
        f"Hiển thị {start_index} - {min(end_index, total_products)} truyện trong tổng số {total_products} truyện"
        if total_products > 0
        else "Không có truyện nào phù hợp"
    )

    # Lấy danh sách thể loại
    categories = Category.objects.filter(is_active=True).annotate(
        active_comic_count=Count("products", filter=Q(products__is_active=True))
    )

    return render(
        request,
        "comics/comic_categories.html",
        {
            "page_obj": page_obj,
            "display_range": display_range,
            "total_pages": paginator.num_pages,
            "categories": categories,
            "sort": sort,
            "category_slugs": [slug],  # Truyền slug hiện tại
        },
    )


def comic_categories_by_author(request, author):
    # Làm sạch và kiểm tra author
    author_cleaned = author.replace("-", " ").strip()
    if (
        not author_cleaned
        or not Comic.objects.filter(
            is_active=True, author__iexact=author_cleaned
        ).exists()
    ):
        raise Http404("Tác giả không tồn tại")

    # Lấy tham số sắp xếp
    sort = request.GET.get("sort", "name_asc")
    sort_field = SORT_MAPPING.get(sort, "name")

    # Lấy danh sách truyện theo author và sắp xếp
    comics = (
        Comic.objects.filter(is_active=True, author__iexact=author_cleaned)
        .select_related("category")
        .order_by(sort_field)
    )

    # Phân trang
    products_per_page = 6
    paginator = Paginator(comics, products_per_page)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Tính toán thông tin hiển thị
    start_index = page_obj.start_index()
    end_index = page_obj.end_index()
    total_products = paginator.count
    display_range = (
        f"Hiển thị {start_index} - {min(end_index, total_products)} truyện trong tổng số {total_products} truyện"
        if total_products > 0
        else "Không có truyện nào phù hợp"
    )

    # Lấy danh sách thể loại
    categories = Category.objects.filter(is_active=True).annotate(
        active_comic_count=Count("products", filter=Q(products__is_active=True))
    )

    return render(
        request,
        "comics/comic_categories.html",
        {
            "page_obj": page_obj,
            "display_range": display_range,
            "total_pages": paginator.num_pages,
            "categories": categories,
            "sort": sort,
            "category_slugs": [],  # Không truyền slug vì lọc theo author
            "selected_author": author_cleaned,
        },
    )


def comic_categories_by_publisher(request, publisher):
    # Làm sạch và kiểm tra publisher
    publisher_cleaned = publisher.replace("-", " ").strip()
    if (
        not publisher_cleaned
        or not Comic.objects.filter(
            is_active=True, publisher__iexact=publisher_cleaned
        ).exists()
    ):
        raise Http404("Nhà xuất bản không tồn tại")

    # Lấy tham số sắp xếp
    sort = request.GET.get("sort", "name_asc")
    sort_field = SORT_MAPPING.get(sort, "name")

    # Lấy danh sách truyện theo publisher và sắp xếp
    comics = (
        Comic.objects.filter(is_active=True, publisher__iexact=publisher_cleaned)
        .select_related("category")
        .order_by(sort_field)
    )

    # Phân trang
    products_per_page = 6
    paginator = Paginator(comics, products_per_page)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Tính toán thông tin hiển thị
    start_index = page_obj.start_index()
    end_index = page_obj.end_index()
    total_products = paginator.count
    display_range = (
        f"Hiển thị {start_index} - {min(end_index, total_products)} truyện trong tổng số {total_products} truyện"
        if total_products > 0
        else "Không có truyện nào phù hợp"
    )

    # Lấy danh sách thể loại
    categories = Category.objects.filter(is_active=True).annotate(
        active_comic_count=Count("products", filter=Q(products__is_active=True))
    )

    return render(
        request,
        "comics/comic_categories.html",
        {
            "page_obj": page_obj,
            "display_range": display_range,
            "total_pages": paginator.num_pages,
            "categories": categories,
            "sort": sort,
            "category_slugs": [],  # Không truyền slug vì lọc theo publisher
            "selected_publisher": publisher_cleaned,
        },
    )


def comic_categories_by_price(request, min_price, max_price=None):
    # Kiểm tra giá hợp lệ
    try:
        min_price_val = int(min_price)
        max_price_val = int(max_price) if max_price is not None else None
        if max_price_val is not None and min_price_val > max_price_val:
            raise Http404("Giá tối thiểu không được lớn hơn giá tối đa")
    except ValueError:
        raise Http404("Giá không hợp lệ")

    # Lấy tham số sắp xếp
    sort = request.GET.get("sort", "name_asc")
    sort_field = SORT_MAPPING.get(sort, "name")

    # Lấy danh sách truyện theo khoảng giá và sắp xếp
    comics = Comic.objects.filter(is_active=True, price__gte=min_price_val)
    if max_price_val is not None:
        comics = comics.filter(price__lte=max_price_val)
    comics = comics.order_by(sort_field)

    # Phân trang
    products_per_page = 6
    paginator = Paginator(comics, products_per_page)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Tính toán thông tin hiển thị
    start_index = page_obj.start_index()
    end_index = page_obj.end_index()
    total_products = paginator.count
    display_range = (
        f"Hiển thị {start_index} - {min(end_index, total_products)} truyện trong tổng số {total_products} truyện"
        if total_products > 0
        else "Không có truyện nào phù hợp"
    )

    # Lấy danh sách thể loại
    categories = Category.objects.filter(is_active=True).annotate(
        active_comic_count=Count("products", filter=Q(products__is_active=True))
    )

    return render(
        request,
        "comics/comic_categories.html",
        {
            "page_obj": page_obj,
            "display_range": display_range,
            "total_pages": paginator.num_pages,
            "categories": categories,
            "sort": sort,
            "category_slugs": [],  # Không truyền slug vì lọc theo giá
            "selected_min_price": min_price,
            "selected_max_price": max_price,
        },
    )
