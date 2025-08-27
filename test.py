from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

docs = ["hành động phiêu lưu", "phiêu lưu khám phá bí ẩn", "tình cảm học đường"]

# Không dùng stopwords để dễ nhìn
vectorizer = TfidfVectorizer()

# Tính TF-IDF
tfidf_matrix = vectorizer.fit_transform(docs)
print("\n Token hóa văn bản tách thành các từ duy nhất.\n")
print(vectorizer.vocabulary_)
feature_names = vectorizer.get_feature_names_out()
print(list(enumerate(feature_names)))

print("\n Số lượng truyện và số chiều vectơ")
print(tfidf_matrix.shape)
print("\n Vectơ hóa mỗi truyện")
print(tfidf_matrix.toarray())
print("\n Kết quả tính tương đồng")

similarity = cosine_similarity(tfidf_matrix, tfidf_matrix)
print(similarity)
