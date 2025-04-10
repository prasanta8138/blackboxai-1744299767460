from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
from collections import defaultdict

app = Flask(__name__)

# Load movie data from CSV
movies_df = pd.read_csv('movies.csv')

def get_recommendations(movie_title):
    """Get movie recommendations based on genre similarity."""
    if movie_title not in movies_df['title'].values:
        return []
    
    # Get the genres of the selected movie
    selected_movie = movies_df[movies_df['title'] == movie_title].iloc[0]
    selected_genres = set(selected_movie['genre'].split(' '))
    
    # Calculate similarity scores
    similarity_scores = []
    for idx, movie in movies_df.iterrows():
        if movie['title'] != movie_title:
            movie_genres = set(movie['genre'].replace(',', '').split(' '))
            # Calculate Jaccard similarity
            if len(selected_genres.union(movie_genres)) > 0:  # Prevent division by zero
                similarity = len(selected_genres.intersection(movie_genres)) / len(selected_genres.union(movie_genres))
            else:
                similarity = 0
            similarity_scores.append((movie['title'], similarity))
    
    # Sort by similarity and get top 5
    recommendations = sorted(similarity_scores, key=lambda x: x[1], reverse=True)[:5]
    recommended_movies = []
    for title, score in recommendations:
        movie = movies_df[movies_df['title'] == title].iloc[0]
        recommended_movies.append({
            'title': str(movie['title']),
            'genre': str(movie['genre']),
            'year': int(movie['year']),
            'rating': float(movie['rating']),
            'description': str(movie['description'])
        })
    
    return recommended_movies

@app.route('/')
def home():
    """Render the home page."""
    return render_template('index.html', movies=movies_df.to_dict('records'))

@app.route('/api/search')
def search():
    """Search for movies."""
    query = request.args.get('query', '').lower()
    if query:
        results = movies_df[movies_df['title'].str.lower().str.contains(query)].to_dict('records')
        return jsonify(results)
    return jsonify([])

@app.route('/api/recommend')
def recommend():
    """Get movie recommendations."""
    movie_title = request.args.get('title', '')
    recommendations = get_recommendations(movie_title)
    return jsonify(recommendations)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
