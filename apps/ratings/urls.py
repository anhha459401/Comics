from django.urls import path
from . import views

app_name = "ratings"

urlpatterns = [
    path("add/<int:comic_id>", views.add_rating, name="add_rating"),
    path("rating-data/<int:comic_id>", views.get_rating_data, name="get_rating_data"),
    path("reviews/<int:comic_id>", views.get_reviews, name="get_reviews"),
]
