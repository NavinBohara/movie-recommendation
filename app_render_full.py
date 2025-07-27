# app_render_full.py - Full ML functionality for Render deployment

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from flask import Flask, render_template, request, jsonify
import json
from functools import lru_cache
import time
import os
import threading

app = Flask(__name__)

# Global variables
movies = None
ratings = None
user_movie_matrix = None
content_similarity = None
movie_indices = None
user_similarity_df = None
data_loaded = False
loading = False

def load_data_background():
    """Load data in background thread for Render"""
    global movies, ratings, user_movie_matrix, content_similarity, movie_indices, user_similarity_df, data_loaded, loading
    
    if data_loaded or loading:
        return
    
    loading = True
    
    try:
        print("Loading data in background...")
        
        # Try different CSV parsing methods
        try:
            movies = pd.read_csv("movies.csv", engine='python', quoting=1)
        except:
            try:
                movies = pd.read_csv("movies.csv", engine='python', quoting=3)
            except:
                movies = pd.read_csv("movies.csv", engine='c', quoting=1)
        
        ratings = pd.read_csv("ratings.csv")
        
        print(f"Successfully loaded {len(movies)} movies and {len(ratings)} ratings")
        
        # Merge ratings with movie titles
        data = pd.merge(ratings, movies, on='movieId')
        
        # Pivot user-item matrix
        user_movie_matrix = data.pivot_table(index='userId', columns='title', values='rating')
        
        # Pre-compute Content-Based Similarity
        print("Computing content-based similarity...")
        movies['genres'] = movies['genres'].fillna('')
        tfidf = TfidfVectorizer(stop_words='english')
        tfidf_matrix = tfidf.fit_transform(movies['genres'])
        content_similarity = cosine_similarity(tfidf_matrix)
        
        # Map movie titles to index
        movie_indices = pd.Series(movies.index, index=movies['title']).drop_duplicates()
        
        # Pre-compute Collaborative Filtering
        print("Computing collaborative filtering similarity...")
        user_movie_matrix_filled = user_movie_matrix.fillna(0)
        user_similarity = cosine_similarity(user_movie_matrix_filled)
        user_similarity_df = pd.DataFrame(user_similarity, index=user_movie_matrix.index, columns=user_movie_matrix.index)
        
        data_loaded = True
        loading = False
        print("Movie Recommender System initialized successfully!")
        print(f"Loaded {len(movies)} movies and {len(ratings)} ratings")
        print(f"Available users: {len(user_movie_matrix.index)}")
        
    except Exception as e:
        print(f"Error loading data: {e}")
        print("Creating sample data for testing...")
        
        # Create sample data if loading fails
        movies = pd.DataFrame({
            'movieId': [1, 2, 3, 4, 5],
            'title': ['Sample Movie 1', 'Sample Movie 2', 'Sample Movie 3', 'Sample Movie 4', 'Sample Movie 5'],
            'genres': ['Action', 'Drama', 'Comedy', 'Sci-Fi', 'Thriller']
        })
        
        ratings = pd.DataFrame({
            'userId': [1, 1, 1, 2, 2, 2, 3, 3, 3],
            'movieId': [1, 2, 3, 1, 2, 4, 2, 3, 5],
            'rating': [5.0, 4.5, 4.0, 4.0, 5.0, 3.5, 4.5, 4.0, 4.5]
        })
        
        # Create user-movie matrix
        data = pd.merge(ratings, movies, on='movieId')
        user_movie_matrix = data.pivot_table(index='userId', columns='title', values='rating')
        
        # Create similarity matrices
        tfidf = TfidfVectorizer(stop_words='english')
        tfidf_matrix = tfidf.fit_transform(movies['genres'])
        content_similarity = cosine_similarity(tfidf_matrix)
        
        movie_indices = pd.Series(movies.index, index=movies['title']).drop_duplicates()
        
        user_movie_matrix_filled = user_movie_matrix.fillna(0)
        user_similarity = cosine_similarity(user_movie_matrix_filled)
        user_similarity_df = pd.DataFrame(user_similarity, index=user_movie_matrix.index, columns=user_movie_matrix.index)
        
        data_loaded = True
        loading = False
        print("Sample data created successfully!")

def ensure_data_loaded():
    """Ensure data is loaded"""
    if not data_loaded and not loading:
        # Start loading in background
        thread = threading.Thread(target=load_data_background)
        thread.daemon = True
        thread.start()
        return False
    return data_loaded

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

def get_hybrid_recommendations(user_id, top_n=3):
    """Get hybrid recommendations"""
    if not ensure_data_loaded():
        return []
    
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
        
        # Compute recommendations
        for movie in user_ratings.index[:10]:  # Limit to top 10 rated movies for performance
            try:
                idx = movie_indices[movie]
                content_scores = content_similarity[idx]
                
                collab_scores = user_movie_matrix.loc[similar_users.index].fillna(0).T.dot(similar_users)
                
                for i, content_score in enumerate(content_scores):
                    title = movies.iloc[i]['title']
                    if title in unrated_movies:
                        collab_score = collab_scores.get(title, 0)
                        final_score = 0.5 * content_score + 0.5 * collab_score
                        scores[title] = final_score
                        
            except (KeyError, IndexError):
                continue
        
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        print(f"Recommendation computation time: {time.time() - start_time:.3f} seconds")
        return sorted_scores[:top_n]
        
    except Exception as e:
        print(f"Error in recommendations: {e}")
        return []

def get_user_ratings(user_id):
    """Get user ratings"""
    if not ensure_data_loaded():
        return []
    
    try:
        user_ratings = user_movie_matrix.loc[user_id].dropna()
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
    """Main page"""
    try:
        ensure_data_loaded()
        if data_loaded:
            user_ids = list(user_movie_matrix.index)
            return render_template('index.html', user_ids=user_ids)
        else:
            return render_template('loading.html')
    except Exception as e:
        return f"Error loading page: {e}", 500

@app.route('/get_recommendations', methods=['POST'])
def get_recommendations():
    """Get recommendations endpoint"""
    try:
        if not data_loaded:
            return jsonify({'error': 'Data still loading, please try again in a moment'}), 503
        
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
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_user_ratings', methods=['POST'])
def get_user_ratings_route():
    """Get user ratings endpoint"""
    try:
        if not data_loaded:
            return jsonify({'error': 'Data still loading, please try again in a moment'}), 503
        
        user_id = int(request.form['user_id'])
        ratings = get_user_ratings(user_id)
        return jsonify(ratings)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy', 
        'message': 'Movie Recommender System is running',
        'data_loaded': data_loaded,
        'loading': loading
    })

@app.route('/ready')
def ready_check():
    """Ready check endpoint"""
    if data_loaded:
        return jsonify({
            'status': 'ready', 
            'message': 'Data loaded successfully',
            'movies_count': len(movies) if movies is not None else 0,
            'users_count': len(user_movie_matrix.index) if user_movie_matrix is not None else 0
        })
    elif loading:
        return jsonify({'status': 'loading', 'message': 'Data is being loaded in background'}), 503
    else:
        return jsonify({'status': 'starting', 'message': 'Starting data loading'}), 503

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting app on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False) 