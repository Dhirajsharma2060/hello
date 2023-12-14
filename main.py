from fastapi import FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import base64
from typing import List, Optional
import requests
from fastapi.responses import FileResponse
import os

app = FastAPI()

# Add CORS middleware to allow requests from your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],  # Update this with the origin of your frontend
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# OpenWeatherMap API key
weather_api_key = '119c5fbb45c75c23bd2e619d97593468'

# Spotify API credentials
spotify_client_id = 'CLIENT_ID'
spotify_client_secret = 'CLIENT_SCERECT'

# Spotify API endpoints
spotify_token_url = 'https://accounts.spotify.com/api/token'
spotify_recommendations_url = 'https://api.spotify.com/v1/recommendations'

@app.get("/")
def read_root():
    return {"message": "Hello, this is your FastAPI backend!"}

@app.post("/recommend")
async def recommend(latitude: float, longitude: float):
    try:
        # Use OpenWeatherMap API to get weather data
        weather_url = f'http://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={weather_api_key}'
        weather_data = requests.get(weather_url).json()

        # Extract relevant weather information (e.g., temperature)
        temperature = weather_data['main']['temp']

        # Get Spotify access token
        spotify_token = get_spotify_token()

        # Get music genre based on temperature
        music_genre = recommend_music_genre(temperature)

        # Get Spotify recommendations based on music genre
        spotify_recommendations = get_spotify_recommendations(spotify_token, music_genre)

        return {
            "recommendation": music_genre,
            "tracks": spotify_recommendations['tracks']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def get_spotify_token():
    # Obtain Spotify access token using client ID and client secret
    headers = {
        'Authorization': 'Basic ' + base64.b64encode(f'{spotify_client_id}:{spotify_client_secret}'.encode()).decode(),
    }
    data = {
        'grant_type': 'client_credentials'
    }
    response = requests.post(spotify_token_url, headers=headers, data=data)
    return response.json().get('access_token', '')

def recommend_music_genre(temperature):
    if temperature > 25:
        return "pop"
    elif 15 <= temperature <= 25:
        return "rock"
    else:
        return "classical"

def get_spotify_recommendations(token, genre):
    # Get Spotify recommendations based on the music genre
    headers = {
        'Authorization': 'Bearer ' + token,
    }
    params = {
        'seed_genres': genre,
        'limit': 5  # Adjust the limit as needed
    }
    response = requests.get(spotify_recommendations_url, headers=headers, params=params)
    return response.json()
