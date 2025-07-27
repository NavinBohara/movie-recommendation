# app_simple.py - Simplified version for deployment

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from flask import Flask, render_template, request, jsonify
import json
import time
import os

app = Flask(__name__)

# Global variables
movies = None
ratings = None
user_movie_matrix = None
content_similarity = None
movie_indices = None
user_similarity_df = None
data_loaded = False

def load_data():
    """Load data on demand"""
    global movies, ratings, user_movie_matrix, content_similarity, movie_indices, user_similarity_df, data_loaded
    
    if data_loaded:
        return
    
    try:
        print("Loading data...")
        movies = pd.read_csv("movies.csv", engine='python')
        ratings = pd.read_csv("ratings.csv")
        
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
        print("Movie Recommender System initialized successfully!")
        print(f"Loaded {len(movies)} movies and {len(ratings)} ratings")
        print(f"Available users: {len(user_movie_matrix.index)}")
        
    except Exception as e:
        print(f"Error loading data: {e}")
        raise e

def get_hybrid_recommendations(user_id, top_n=3):
    """Get hybrid recommendations"""
    start_time = time.time()
    
    try:
        # Load data if not loaded
        if not data_loaded:
            load_data()
        
        # Get user ratings
        user_ratings = user_movie_matrix.loc[user_id].dropna()
        
        if user_ratings.empty:
            return []
        
        # Get similar users
        similar_users = user_similarity_df[user_id].sort_values(ascending=False)[1:11]
        
        # Initialize scores dictionary
        scores = {}
        
        # Get movies the user hasn't rated
        all_movies = set(movies['title'])
        rated_movies = set(user_ratings.index)
        unrated_movies = all_movies - rated_movies
        
        # Compute recommendations
        for movie in user_ratings.index[:10]:
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
    try:
        if not data_loaded:
            load_data()
        
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
        if not data_loaded:
            load_data()
        user_ids = list(user_movie_matrix.index)
        return render_template('index.html', user_ids=user_ids)
    except Exception as e:
        return f"Error loading page: {e}", 500

@app.route('/get_recommendations', methods=['POST'])
def get_recommendations():
    """Get recommendations endpoint"""
    try:
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
        user_id = int(request.form['user_id'])
        ratings = get_user_ratings(user_id)
        return jsonify(ratings)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Movie Recommender System is running'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False) 