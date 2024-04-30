from flask import Flask, redirect, request, jsonify, session
import requests
from datetime import datetime, timedelta

API_BASE_URL= 'https://api.spotify.com/v1/'

def get_playlist():
    if 'access_token' not in session:
        return redirect('/login')
        
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh_token')
        
    headers={
        'Authorization': f"Bearer {session['access_token']}"
    }  
    
    response= requests.get(API_BASE_URL + 'me/playlists', headers=headers)
    playlists=response.json()
    playlist_names = [playlist['name'] for playlist in playlists['items']]

    
    return jsonify(playlist_names) 
    
def userDetails():
     if 'access_token' not in session:
        return redirect('/login')

    # Get user information from Spotify API
     headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }
     response = requests.get(API_BASE_URL + 'me', headers=headers)
     user_info = response.json()

    # Extract user ID and display name
     user_id = user_info['id']
     display_name = user_info['display_name']
     profile_image = user_info.get('images', [{'url': None}])[0]['url']
     
     return jsonify({'user_id': user_id, 'display_name': display_name, 'profile_image': profile_image})


    
    
