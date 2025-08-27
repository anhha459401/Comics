import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from apps.comics.models import Comic
from apps.ratings.models import Rating
from apps.favorites.models import Favorite
from apps.comics.models import ViewHistory


def get_content_based_recommendations(user_id, comic_id, num_recommendations=10):
    # Lấy danh sách truyện mà user đã tương tác
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
    print(f"[DEBUG] interacted_comics: {interacted_comics}")

    # Lấy tất cả truyện chưa tương tác
    comics = Comic.objects.filter(is_active=True).exclude(id__in=interacted_comics)
    comic_data = []
    for comic in comics:
        features = f"{comic.category.name} {comic.author} {comic.publisher or ''} {comic.description or ''}"
        comic_data.append({"id": comic.id, "features": features})

    # Thêm truyện đầu vào vào tập dữ liệu để tính similarity
    try:
        input_comic = Comic.objects.get(id=comic_id, is_active=True)
        comic_data.append(
            {
                "id": input_comic.id,
                "features": f"{input_comic.category.name} {input_comic.author} {input_comic.publisher or ''} {input_comic.description or ''}",
            }
        )
    except Comic.DoesNotExist:
        pass

    # Tạo DataFrame
    df = pd.DataFrame(comic_data)
    print(f"[DEBUG] DataFrame:\n{df}\n")

    # Stopwords tiếng Việt
    vietnamese_stopwords = [
        "là",
        "và",
        "của",
        "có",
        "một",
        "những",
        "được",
        "trong",
        "khi",
        "với",
        "vì",
        "cho",
        "này",
        "kia",
        "đó",
        "thì",
        "ra",
        "từ",
        "đến",
        "cũng",
        "nên",
    ]

    # Tính TF-IDF
    tfidf = TfidfVectorizer(stop_words=vietnamese_stopwords)
    tfidf_matrix = tfidf.fit_transform(df["features"])
    print(f"[DEBUG] TF-IDF Vocabulary:\n{tfidf.vocabulary_}\n")
    print(f"[DEBUG] TF-IDF Shape: {tfidf_matrix.shape}")
    print(f"[DEBUG] TF-IDF Matrix:\n{tfidf_matrix.toarray()}\n")

    # Tính cosine similarity
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
    print(f"[DEBUG] Cosine Similarity Matrix:\n{cosine_sim}\n")

    # Tìm index của truyện đầu vào
    idx = df[df["id"] == comic_id].index[0] if comic_id in df["id"].values else -1
    if idx == -1:
        print("[WARNING] comic_id không tồn tại trong dữ liệu TF-IDF")
        return (
            Comic.objects.filter(is_active=True)
            .exclude(id__in=interacted_comics)
            .exclude(id=comic_id)
            .order_by("-created_at")[:num_recommendations]
        )

    # Tính độ tương tự của truyện đầu vào với các truyện khác
    sim_scores = list(enumerate(cosine_sim[idx]))
    print(f"[DEBUG] Raw Similarity Scores: {sim_scores}\n")

    # Sắp xếp theo độ tương tự giảm dần
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    print(f"[DEBUG] Sorted Similarity Scores: {sim_scores}\n")

    # Loại bỏ chính nó và chỉ lấy top N
    sim_scores = [(i, score) for i, score in sim_scores if df.iloc[i]["id"] != comic_id]
    sim_scores = sim_scores[:num_recommendations]
    print(f"[DEBUG] Final Top {num_recommendations} Scores: {sim_scores}\n")

    # Lấy ID truyện gợi ý
    comic_indices = [i[0] for i in sim_scores]
    recommended_comic_ids = df.iloc[comic_indices]["id"].values
    print(f"[DEBUG] Recommended Comic IDs: {recommended_comic_ids}\n")

    return Comic.objects.filter(id__in=recommended_comic_ids).exclude(
        id__in=interacted_comics
    )
