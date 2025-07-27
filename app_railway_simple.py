# app_railway_simple.py - Ultra-simple Railway deployment version

from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)

# Global variables
data_loaded = False
movies = None
ratings = None
user_movie_matrix = None

@app.route('/')
def index():
    """Main page - always works"""
    return render_template('index_simple.html')

@app.route('/health')
def health_check():
    """Health check endpoint - always returns success"""
    return jsonify({
        'status': 'healthy', 
        'message': 'Movie Recommender System is running',
        'data_loaded': data_loaded
    }), 200

@app.route('/ready')
def ready_check():
    """Ready check endpoint"""
    return jsonify({
        'status': 'ready', 
        'message': 'Application is ready'
    }), 200

@app.route('/test')
def test():
    """Simple test endpoint"""
    return jsonify({
        'message': 'Test endpoint working!',
        'port': os.environ.get('PORT', '5000')
    }), 200

@app.route('/get_recommendations', methods=['POST'])
def get_recommendations():
    """Get recommendations endpoint - simplified"""
    try:
        user_id = int(request.form['user_id'])
        # Return sample recommendations for now
        sample_recommendations = [
            {'title': 'Sample Movie 1', 'score': 0.95, 'genre': 'Action'},
            {'title': 'Sample Movie 2', 'score': 0.88, 'genre': 'Drama'},
            {'title': 'Sample Movie 3', 'score': 0.82, 'genre': 'Comedy'}
        ]
        return jsonify(sample_recommendations)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_user_ratings', methods=['POST'])
def get_user_ratings_route():
    """Get user ratings endpoint - simplified"""
    try:
        user_id = int(request.form['user_id'])
        # Return sample ratings for now
        sample_ratings = [
            {'title': 'Sample Movie A', 'rating': 5.0, 'genre': 'Action'},
            {'title': 'Sample Movie B', 'rating': 4.5, 'genre': 'Drama'},
            {'title': 'Sample Movie C', 'rating': 4.0, 'genre': 'Comedy'}
        ]
        return jsonify(sample_ratings)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting app on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False) 