# 🎬 Movie Recommender System

A beautiful Flask web application that provides AI-powered movie recommendations using hybrid filtering (content-based + collaborative filtering).

## Features

- **Modern UI**: Beautiful, responsive design with animations and gradients
- **Hybrid Recommendations**: Combines content-based and collaborative filtering
- **User Ratings Display**: Shows existing user ratings with star ratings
- **Real-time Recommendations**: Get personalized movie suggestions instantly
- **Mobile Responsive**: Works perfectly on all devices

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the Flask application:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5001
```

3. Select a user ID from the dropdown menu
4. Click "Get Recommendations" to see personalized movie suggestions

## How It Works

### Data Processing
- Loads movie data from `movies.csv` (movie titles and genres)
- Loads rating data from `ratings.csv` (user ratings)
- Creates user-item matrix for collaborative filtering

### Recommendation Algorithm
1. **Content-Based Filtering**: Uses TF-IDF vectorization of movie genres to find similar movies
2. **Collaborative Filtering**: Finds similar users based on rating patterns
3. **Hybrid Approach**: Combines both methods with equal weights (50% each)

### Features
- **User Selection**: Choose from available user IDs
- **Rating Display**: View all movies rated by the selected user
- **Recommendations**: Get top 3 movie recommendations with scores
- **Beautiful UI**: Modern design with smooth animations

## File Structure

```
movie/
├── app.py              # Main Flask application
├── movies.csv          # Movie data (titles, genres)
├── ratings.csv         # User rating data
├── requirements.txt    # Python dependencies
├── templates/
│   └── index.html     # Main HTML template
└── static/
    ├── css/
    │   └── style.css  # CSS styles
    └── js/
        └── script.js  # JavaScript functionality
```

## Technologies Used

- **Backend**: Flask, Python
- **Frontend**: HTML5, CSS3, JavaScript
- **Machine Learning**: scikit-learn, pandas, numpy
- **Styling**: Custom CSS with gradients and animations
- **Icons**: Font Awesome
- **Fonts**: Google Fonts (Poppins)

## API Endpoints

- `GET /`: Main page with user selection
- `POST /get_recommendations`: Get movie recommendations for a user
- `POST /get_user_ratings`: Get all ratings for a specific user

## Customization

You can easily customize the application by:
- Modifying the CSS in `static/css/style.css` for different styling
- Adjusting the recommendation algorithm in `app.py`
- Adding more features in the JavaScript file `static/js/script.js`
- Updating the HTML template in `templates/index.html`

## Troubleshooting

- If port 5000 is in use, the app will automatically use port 5001
- Make sure all CSV files are in the correct format
- Ensure all dependencies are installed correctly

Enjoy discovering new movies! 🍿 