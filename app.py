# app.py

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from flask import Flask, render_template, request, jsonify
import json
from functools import lru_cache
import time

app = Flask(__name__)

# ===== Load Data =====
print("Loading data...")
movies = pd.read_csv("movies.csv", engine='python')  # Use python engine for better CSV handling
ratings = pd.read_csv("ratings.csv")

# Merge ratings with movie titles
data = pd.merge(ratings, movies, on='movieId')

# Pivot user-item matrix
user_movie_matrix = data.pivot_table(index='userId', columns='title', values='rating')

# ===== Pre-compute Content-Based Similarity =====
print("Computing content-based similarity...")
movies['genres'] = movies['genres'].fillna('')
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(movies['genres'])

# Compute cosine similarity between movies (pre-computed)
content_similarity = cosine_similarity(tfidf_matrix)

# Map movie titles to index
movie_indices = pd.Series(movies.index, index=movies['title']).drop_duplicates()

# ===== Pre-compute Collaborative Filtering =====
print("Computing collaborative filtering similarity...")
user_movie_matrix_filled = user_movie_matrix.fillna(0)
user_similarity = cosine_similarity(user_movie_matrix_filled)
user_similarity_df = pd.DataFrame(user_similarity, index=user_movie_matrix.index, columns=user_movie_matrix.index)

# ===== Cache for better performance =====
@lru_cache(maxsize=128)
def get_cached_user_ratings(user_id):
    """Cache user ratings to avoid repeated computation"""
    try:
        user_ratings = user_movie_matrix.loc[user_id].dropna()
        return user_ratings
    except:
        return pd.Series()

@lru_cache(maxsize=128)
def get_cached_similar_users(user_id):
    """Cache similar users computation"""
    try:
        similar_users = user_similarity_df[user_id].sort_values(ascending=False)[1:11]  # Top 10 similar users
        return similar_users
    except:
        return pd.Series()

# ===== Optimized Hybrid Recommendation Function =====
def get_hybrid_recommendations(user_id, top_n=3):
    start_time = time.time()
    
    try:
        # Get cached user ratings
        user_ratings = get_cached_user_ratings(user_id)
        
        if user_ratings.empty:
            return []
        
        # Get cached similar users
        similar_users = get_cached_similar_users(user_id)
        
        # Initialize scores dictionary
        scores = {}
        
        # Get movies the user hasn't rated
        all_movies = set(movies['title'])
        rated_movies = set(user_ratings.index)
        unrated_movies = all_movies - rated_movies
        
        # Limit computation to top similar users and unrated movies
        for movie in user_ratings.index[:10]:  # Limit to top 10 rated movies for efficiency
            try:
                idx = movie_indices[movie]
                content_scores = content_similarity[idx]
                
                # Get collaborative scores from similar users
                collab_scores = user_movie_matrix.loc[similar_users.index].fillna(0).T.dot(similar_users)
                
                # Combine scores for unrated movies only
                for i, content_score in enumerate(content_scores):
                    title = movies.iloc[i]['title']
                    if title in unrated_movies:
                        collab_score = collab_scores.get(title, 0)
                        final_score = 0.5 * content_score + 0.5 * collab_score
                        scores[title] = final_score
                        
            except (KeyError, IndexError):
                continue
        
        # Sort and return top recommendations
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        print(f"Recommendation computation time: {time.time() - start_time:.3f} seconds")
        return sorted_scores[:top_n]
        
    except Exception as e:
        print(f"Error in recommendations: {e}")
        return []

def get_user_ratings(user_id):
    try:
        user_ratings = get_cached_user_ratings(user_id)
        ratings_list = []
        
        for movie, rating in user_ratings.items():
            genre = movies[movies['title'] == movie]['genres'].values[0]
            ratings_list.append({
                'title': movie,
                'rating': rating,
                'genre': genre
            })
        return ratings_list
    except:
        return []

@app.route('/')
def index():
    user_ids = list(user_movie_matrix.index)
    return render_template('index.html', user_ids=user_ids)

@app.route('/get_recommendations', methods=['POST'])
def get_recommendations():
    user_id = int(request.form['user_id'])
    recommendations = get_hybrid_recommendations(user_id, 3)
    
    recommendations_list = []
    for title, score in recommendations:
        genre = movies[movies['title'] == title]['genres'].values[0]
        recommendations_list.append({
            'title': title,
            'score': round(score, 3),
            'genre': genre
        })
    
    return jsonify(recommendations_list)

@app.route('/get_user_ratings', methods=['POST'])
def get_user_ratings_route():
    user_id = int(request.form['user_id'])
    ratings = get_user_ratings(user_id)
    return jsonify(ratings)

if __name__ == '__main__':
    print("Movie Recommender System initialized successfully!")
    print(f"Loaded {len(movies)} movies and {len(ratings)} ratings")
    print(f"Available users: {len(user_movie_matrix.index)}")
    app.run(debug=True, port=5001)
