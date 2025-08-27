from apps.comics.models import Category, Comic
from apps.cart.models import Cart


def navigation_data(request):
    categories = Category.objects.filter(is_active=True).order_by("name")
    authors = Comic.objects.filter(is_active=True).values("author").distinct()
    publishers = Comic.objects.filter(is_active=True).values("publisher").distinct()
    price_ranges = [
        {"name": "Dưới 50,000đ", "min": 0, "max": 50000},
        {"name": "50,000 - 100,000đ", "min": 50000, "max": 100000},
        {"name": "100,000 - 200,000đ", "min": 100000, "max": 200000},
        {"name": "Trên 200,000đ", "min": 200000, "max": None},
    ]
    return {
        "categories": categories,
        "authors": authors,
        "publishers": publishers,
        "price_ranges": price_ranges,
    }


def cart(request):
    cart_items = []
    total_price = 0
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user).select_related("comic")
        total_price = sum(item.total_price for item in cart_items)
    return {"cart_items": cart_items, "total_price": total_price}
