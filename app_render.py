# app_render.py - Ultra-simple Render deployment version

from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)

@app.route('/')
def index():
    """Main page - always works"""
    return render_template('render_success.html')

@app.route('/health')
def health_check():
    """Health check endpoint - always returns success"""
    return jsonify({
        'status': 'healthy', 
        'message': 'Movie Recommender System is running on Render',
        'port': os.environ.get('PORT', '5000')
    }), 200

@app.route('/ready')
def ready_check():
    """Ready check endpoint"""
    return jsonify({
        'status': 'ready', 
        'message': 'Application is ready and running'
    }), 200

@app.route('/test')
def test():
    """Simple test endpoint"""
    return jsonify({
        'message': 'Test endpoint working on Render!',
        'port': os.environ.get('PORT', '5000'),
        'environment': 'Render'
    }), 200

@app.route('/api/status')
def api_status():
    """API status endpoint"""
    return jsonify({
        'service': 'Movie Recommender System',
        'status': 'operational',
        'deployment': 'Render',
        'version': '1.0.0'
    }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting app on port {port}")
    print(f"Environment: {os.environ.get('RENDER', 'local')}")
    app.run(host='0.0.0.0', port=port, debug=False) 