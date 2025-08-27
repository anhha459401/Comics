from django.urls import path
from . import views

app_name = "comics"

urlpatterns = [
    path("", views.comic_list, name="comic_list"),
    # path("track-view", views.track_view, name="track_view"),
    path("search", views.search_comics, name="search_comics"),
    path("history", views.view_history, name="view_history"),
    path("<slug:slug>", views.comic_detail, name="comic_detail"),
    path(
        "categories/<slug:slug>",
        views.comic_categories_by_slug,
        name="comic_categories_by_slug",
    ),
    path(
        "author/<str:author>",
        views.comic_categories_by_author,
        name="comic_categories_by_author",
    ),
    path(
        "publisher/<str:publisher>",
        views.comic_categories_by_publisher,
        name="comic_categories_by_publisher",
    ),
    path(
        "price/<int:min_price>",
        views.comic_categories_by_price,
        name="comic_categories_by_price",
    ),
    path(
        "price/<int:min_price>/<int:max_price>",
        views.comic_categories_by_price,
        name="comic_categories_by_price",
    ),
]
