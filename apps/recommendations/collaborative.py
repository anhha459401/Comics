from surprise import SVD, Dataset, Reader
from apps.ratings.models import Rating
from apps.favorites.models import Favorite
from apps.comics.models import Comic, ViewHistory
from apps.accounts.models import UserProfile
import pandas as pd
from django.utils import timezone
import numpy as np


def train_collaborative_filtering(user_id):
    if not user_id:
        print("[INFO] No user_id provided. Training skipped.")
        return None
    try:
        profile = UserProfile.objects.get(user_id=user_id)
        age = profile.age
        gender = profile.gender
        age_range = (max(0, age - 5), age + 5) if age else (0, 100)

        print(
            f"[INFO] Target user: {user_id}, Gender: {gender}, Age: {age}, Age Range: {age_range}"
        )

        similar_users = (
            UserProfile.objects.filter(
                gender=gender,
                date_of_birth__year__gte=timezone.now().year - age_range[1],
                date_of_birth__year__lte=timezone.now().year - age_range[0],
            )
            .exclude(user_id=user_id)
            .values_list("user_id", flat=True)
        )
        print(f"[INFO] Found {len(similar_users)} similar users: {list(similar_users)}")

        ratings = Rating.objects.filter(user_id__in=similar_users)
        favorites = Favorite.objects.filter(user_id__in=similar_users)
        views = ViewHistory.objects.filter(user_id__in=similar_users)
        print(
            f"[INFO] Ratings: {len(ratings)}, Favorites: {len(favorites)}, Views: {len(views)}"
        )

    except UserProfile.DoesNotExist:
        print("[WARN] User profile does not exist.")
        return None

    # Merge data
    rating_data = [(r.user.id, r.comic.id, r.rating) for r in ratings]
    favorite_data = [(f.user.id, f.comic.id, 5.0) for f in favorites]
    view_data = [(v.user.id, v.comic.id, 3.0) for v in views]
    data = rating_data + favorite_data + view_data

    print(f"[INFO] Total data points: {len(data)}")
    if len(data) > 0:
        print("[DEBUG] Sample data:", data[:5])

    df = pd.DataFrame(data, columns=["user_id", "comic_id", "rating"])
    if df.empty:
        print("[WARN] No data available to train model.")
        return None

    # 📌 Print the rating matrix
    rating_matrix = df.pivot_table(
        index="user_id", columns="comic_id", values="rating", fill_value=0
    )

    # In danh sách comic_id tương ứng với cột
    comic_ids = list(rating_matrix.columns)
    print(f"\n[INFO] Comic ID list (column order): {comic_ids}")

    print("\n[INFO] Rating Matrix (rows = users, columns = comics):")
    print(rating_matrix)

    # Train SVD
    reader = Reader(rating_scale=(1, 5))
    dataset = Dataset.load_from_df(df, reader)
    trainset = dataset.build_full_trainset()
    model = SVD()
    model.fit(trainset)
    print("[INFO] Model training complete.")

    # 📌 In ma trận P và Q
    print(f"\n[INFO] User latent matrix P shape: {model.pu.shape}")
    print(model.pu)

    print(f"\n[INFO] Item latent matrix Q shape: {model.qi.shape}")
    print(model.qi)

    # 📌 Tạo ma trận dự đoán đầy đủ (users × items)
    predictions_matrix = np.dot(model.pu, model.qi.T)
    print(f"\n[INFO] Predictions Matrix shape: {predictions_matrix.shape}")
    print(predictions_matrix)

    return model


def get_collaborative_recommendations(user_id, model, num_recommendations=10):
    if not model:
        print("[WARN] No trained model available.")
        return Comic.objects.none()

    user_ratings = Rating.objects.filter(user_id=user_id).values_list(
        "comic_id", flat=True
    )
    user_favorites = Favorite.objects.filter(user_id=user_id).values_list(
        "comic_id", flat=True
    )
    user_views = ViewHistory.objects.filter(user_id=user_id).values_list(
        "comic_id", flat=True
    )
    interacted_comics = set(user_ratings) | set(user_favorites) | set(user_views)
    print(
        f"[INFO] User has interacted with {len(interacted_comics)} comics: {list(interacted_comics)}"
    )

    comics = Comic.objects.filter(is_active=True).exclude(id__in=interacted_comics)
    predictions = [(comic.id, model.predict(user_id, comic.id).est) for comic in comics]

    predictions = sorted(predictions, key=lambda x: x[1], reverse=True)
    recommended_comic_ids = [pred[0] for pred in predictions[:num_recommendations]]
    print(f"[INFO] Recommended comic IDs: {recommended_comic_ids}")
    return Comic.objects.filter(id__in=recommended_comic_ids)
