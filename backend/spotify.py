import requests
import urllib.parse
from sharing import get_playlist,userDetails

from datetime import datetime, timedelta
from flask import Flask, redirect, request, jsonify, session

app = Flask(__name__)
app.secret_key= '53d355f8-571a-4590-a310-1f9579440851'  #research later

CLIENT_ID='a9736e527970462a878ac1113b95d52f'
CLIENT_SECRET='41055803e9c947ee80f9dea38820cb50'
REDIRECT_URI='http://127.0.0.1:5000/callback'
TOKEN_URL='https://accounts.spotify.com/api/token'
AUTH_URL = 'https://accounts.spotify.com/authorize'

@app.route('/')
def index():
    return "Welcome to Spotify <a href='/login'>Login with Spotify</a>"

@app.route('/login')
def login():
    scope = 'user-read-private user-read-email  user-read-playback-state user-modify-playback-state'

    params = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'scope': scope,
        'redirect_uri': REDIRECT_URI,
        'show_dialog': 'true'  # Corrected to string value
    }

    auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"
    return redirect(auth_url)
     
@app.route('/callback')
def callback():
    if 'error' in request.args:
        return jsonify({"error": request.args['error']})
        
    if 'code' in request.args:
        req_body={
            'code': request.args['code'],
            'grant_type': 'authorization_code',
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
          } 
          
        response = requests.post(TOKEN_URL, data=req_body)
        token_info = response.json()
        
        session['access_token'] = token_info['access_token']
        session['refresh_token']=token_info['refresh_token']
        session['expires_at'] = datetime.now().timestamp() + token_info['expires_in']  


        # Handle token_info as needed

        return redirect('/addqueue')



@app.route('/addqueue', methods=['GET','POST'])
def AddQueue():

    url='https://api.spotify.com/v1/me/player/queue?'
    
    access_token=session.get('access_token')
    
    if not access_token:
        print("Access token missing")
        return
    headers={
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json'
    }
    data={
        'uri': "spotify:track:2MF4HtZHBoUliOi9nOAbS0"
    }
    
    response=requests.post(url, headers=headers, params=data)
    
    if response.status_code==204:
        print("Queued bitch!!")
        
        
    else:
        print("Error:", response.status_code, response.text)    
              

    return userDetails()     
    
    

@app.route('/queue', methods =['GET'])
def get_queue():
    if 'access_token' not in session:
        return redirect('/login')
        
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh_token')
        
    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }
    
    response = requests.get(API_BASE_URL + 'me/player/queue', headers=headers)
    queue_data = response.json()
    track_names = [track['name'] for track in queue_data['queue']]
    
    return jsonify(track_names)


@app.route('/refresh_token')
def refresh_token():
    if 'refresh_token' not in session:
        return redirect('/login')  

    if datetime.now().timestamp() > session['expires_at']:
        req_body={
            'grant_type':'refresh_token',
            'refresh_token' : session['refresh_token'],
            'client_id':CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }
        
        response = requests.post(TOKEN_URL, data=req_body)
        new_token_info = response.json()
        
        session['access_token'] = new_token_info['access_token']
        session['expires_at'] = datetime.now().timestamp() + new_token_info['expires_in']
        
        return redirect('/queue') 



if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
    
    
    