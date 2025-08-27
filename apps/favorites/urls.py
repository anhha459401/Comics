from django.urls import path
from . import views

app_name = "favorites"

urlpatterns = [
    path("add/<int:comic_id>", views.add_to_favorite, name="add_to_favorite"),
    path(
        "remove/<int:comic_id>",
        views.remove_from_favorite,
        name="remove_from_favorite",
    ),
    # path(
    #     "check/<int:comic_id>",
    #     views.check_favorite_status,
    #     name="check_favorite_status",
    # ),
    path("total", views.total_favorites, name="total_favorites"),
    path("list", views.favorites_list, name="favorites_list"),
    path(
        "check-multiple",
        views.check_multiple_favorites,
        name="check_multiple_favorites",
    ),
]
