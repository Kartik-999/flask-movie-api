import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Function to fetch movie details from OMDB API
def get_movie_details_from_omdb(movie_name):
    api_key = "44ac3131" #OMDB API KEY got it from OMDB
    url = f"http://www.omdbapi.com/?t={movie_name}&apikey={api_key}"
    response = requests.get(url)
    return response.json()

# Function to fetch a list of all available movies from OMDB API
def get_all_movies_from_omdb():
    api_key ="44ac3131"
    url = f"http://www.omdbapi.com/?s=*&apikey={api_key}"
    response = requests.get(url)
    return response.json()

# Function to validate the API key
def is_valid_api_key(api_key):
    # In a real scenario, you may store the API keys in a secure database
    # For this example, we'll use a hardcoded API key
    valid_api_key = "44ac3131"  # Store the API key in an environment variable
    return api_key == valid_api_key

# Custom decorator for API key validation
def require_api_key(view_func):
    def wrapper(*args, **kwargs):
        api_key = request.headers.get('API-Key')
        if not api_key or not is_valid_api_key(api_key):
            return jsonify({"error": "Unauthorized"}), 401
        return view_func(*args, **kwargs)
    return wrapper

# Endpoint to get movie details by movie name
def get_movie_details(movie_name):
    data = get_movie_details_from_omdb(movie_name)
    if data.get('Response') == 'True':
        movie_details = {
            "title": data.get('Title'),
            "release_year": data.get('Year'),
            "plot": data.get('Plot'),
            "cast": data.get('Actors').split(', '),
            "rating": float(data.get('imdbRating'))
        }
        return jsonify(movie_details)
    else:
        return jsonify({"error": "Movie not found"}), 404

# Endpoint to get a list of all available movies
@app.route('/movies', methods=['GET'])
@require_api_key
def get_all_movies_list():
    data = get_all_movies_from_omdb()
    if data.get('Response') == 'True':
        movies_list = []
        for movie in data.get('Search'):
            movie_details = {
                "title": movie.get('Title'),
                "release_year": movie.get('Year'),
                "imdb_id": movie.get('imdbID')
            }
            movies_list.append(movie_details)
        return jsonify(movies_list)
    else:
        return jsonify({"error": "No movies found"}), 404

# Register the routes
app.add_url_rule('/movies/<string:movie_name>', 'get_movie_details', get_movie_details, methods=['GET'])
app.add_url_rule('/movies', 'get_all_movies_list', get_all_movies_list, methods=['GET'])

if __name__ == '__main__':
    app.run(debug=True)
