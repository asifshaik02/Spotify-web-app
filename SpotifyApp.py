import os
import requests
import base64
from time import sleep 
from dotenv import load_dotenv

load_dotenv()

redirect_url = 'https://spotifywebapp0.herokuapp.com/callback'

# helper functions
def mstosec(t):
    sec = t // 1000
    m = sec // 60
    s = sec % 60
    if m < 10:
        m = f"0{m}"
    if s < 10:
        s = f"0{s}"

    return f"{m}:{s}"


def check_status(res, msg):
    if res.status_code not in [200, 299]:
        raise Exception(f"{msg}\nResponse Code:{res.status_code}")


def listToNames(l):
    name = ''
    for i in l:
        if l.index(i):
            name += ', '
        name += i


class SpotifyUserAuth:

    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRECT')

    auth_url = "https://accounts.spotify.com/authorize"

    # add scopes to get access to different types of data
    def get_auth_data(self):
        return {
            'client_id': self.client_id,
            'response_type': 'code',
            "scope": "user-read-private user-read-email user-follow-read user-follow-modify playlist-read-private playlist-read-collaborative user-top-read user-read-recently-played",
            'redirect_uri': redirect_url
        }

    def get_auth_headers(self):
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
            "Accept-Encoding": "*",
            "Connection": "keep-alive"
        }

    def user_auth(self):
        endpoint = self.auth_url

        auth_data = self.get_auth_data()
        auth_headers = self.get_auth_headers()
        r = requests.get(endpoint, params=auth_data, headers=auth_headers)

        return r.url


class SpotifyClientAuth:

    access_token = None
    expires_in = None
    refresh_token = None

    auth_code = None
    redirect_uri = redirect_url

    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRECT')

    token_url = "https://accounts.spotify.com/api/token"


    def __init__(self,code):
        self.auth_code = code


    def get_creds(self):
        creds = f"{self.client_id}:{self.client_secret}"
        creds64 = base64.b64encode(creds.encode())
        return creds64.decode()

    def get_token_data(self):
        return {
            'grant_type': 'authorization_code',
            'code':self.auth_code,
            'redirect_uri':self.redirect_uri
        }

    def get_token_header(self):
        return{
            'Authorization':f'Basic {self.get_creds()}'
        }

    def client_auth(self):
        endpoint = self.token_url

        token_data = self.get_token_data()
        token_header = self.get_token_header()

        r = requests.post(endpoint, data=token_data, headers=token_header)
        if r.status_code not in [200,299]:
            raise Exception("Authentication failed")
            return False

        data = r.json()
    
        self.access_token = data['access_token']
        self.expires_in = data['expires_in']
        self.refresh_token = data['refresh_token']

        return True

    def get_access_token(self):
        return self.access_token
    
    def get_user(self):
        return CurrentUser(self.get_access_token())
    
    def get_track(self,_id):
        return Track(self.get_access_token(),_id)
    
    def get_artist(self, _id):
        return Artist(self.get_access_token(), _id)

    def get_playlist(self,_id):
        return Playlist(self.get_access_token(),_id)

    def get_home(self):
        return Browse(self.get_access_token())
    
    def search(self,q):
        return Search(self.get_access_token(),q)


class CurrentUser:
    access_token = None
    base_url = 'https://api.spotify.com/v1/me/'

    user_name = ''
    user_id = ''
    user_img = ''

    open_in_spotify = ''    # link to user's spotify account

    followers_count = ''
    following_count = ''
    playlist_count = ''

    top_artists_list = []   # list of dict containing artist's name,id,img_url
    top_tracks_list = []    # list of dict containing Track's name,id,img_url,artist_list

    playlist = []   # list of dict containing playlits's id,name,img_url,no.of tracks

    recently_played = []    # user's recently played tracks

    def __init__(self,token):
        self.access_token = token
        self.get_user_details()
        self.get_user_top_artists()
        self.get_user_top_tracks()
        self.get_user_playlist()
        self.get_user_following()
        self.get_recent()

    def get_headers(self):
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        return headers
    
    
    def get_user_details(self):
        headers = self.get_headers()
        endpoint = self.base_url

        r = requests.get(endpoint,headers=headers)

        check_status(r, 'Falied to get user data')
        
        data = r.json()

        self.user_name = data['display_name']
        self.user_id = data['id']
        try:
            self.user_img = data['images'][0]['url']
        except:
            self.user_img = None

        self.open_in_spotify = data['external_urls']['spotify']

        self.followers_count = data['followers']['total']

    def get_user_top(self,_type):
        headers = self.get_headers()
        endpoint = self.base_url + f'top/{_type}?limit=8'
        r = requests.get(endpoint, headers=headers)

        check_status(r, f'Falied to get {_type} data')


        return r.json()['items']
    
    def get_user_top_tracks(self):
        data = self.get_user_top('tracks')

        
        for item in data:
            track = {}
            track['id'] = item['id']
            track['name'] = item['name']
            track['time'] = mstosec(item['duration_ms'])
            track['album_name'] = item['album']['name']
            track['artists'] = ''
            for i in item['artists']:
                if item['artists'].index(i):
                    track['artists'] += ', '
                track['artists'] += i['name']

            track['img'] = item['album']['images'][0]['url']

            self.top_tracks_list.append(track)
    
    def get_user_top_artists(self):
        data = self.get_user_top('artists')


        for item in data:
            artist = {}
            artist['id'] = item['id']
            artist['name'] = item['name']
            artist['img'] = item['images'][0]['url']

            self.top_artists_list.append(artist)

    def get_user_playlist(self):
        headers = self.get_headers()
        endpoint = self.base_url + 'playlists'
        r = requests.get(endpoint, headers=headers)

        check_status(r,"Failed to load user's playlist data")

        data = r.json()

        self.playlist_count = data['total']
        # print(self.playlist_count)


        for item in data['items']:
            play_dict = {}
            play_dict['id'] = item['id']
            play_dict['name'] = item['name']
            play_dict['img'] = item['images'][0]['url']

            self.playlist.append(play_dict)

    def get_user_following(self):
        headers = self.get_headers()
        endpoint = self.base_url + 'following?type=artist'

        r = requests.get(endpoint, headers=headers)

        check_status(r,"failed to load user's following count")

        self.following_count = r.json()['artists']['total']

    def get_recent(self):
        headers = self.get_headers()
        endpoint = self.base_url + 'player/recently-played?limit=15'

        r = requests.get(endpoint, headers=headers)

        check_status(r,"Failed to load recently played Tracks")

        data = r.json()['items']
        # print(data)


        for item in data:
            recent = {}
            recent['id'] = item['track']['id']
            recent['name'] = item['track']['name']
            recent['img'] = item['track']['album']['images'][0]['url']
            recent['album_name'] = item['track']['album']['name']
            recent['time'] = mstosec(item['track']['duration_ms'])
            recent['artist'] = ''

            for i in item['track']['artists']:
                if item['track']['artists'].index(i):
                    recent['artist'] += ', '
                recent['artist'] += i['name']

            self.recently_played.append(recent)
        # print(self.recently_played)

 
class Artist:

    access_token = None
    base_url = 'https://api.spotify.com/v1/artists/'

    artist_id = ''
    artist_name = ''
    artist_img = ''

    followers = ''
    popularity = '' # in percentage

    def __init__(self,token,_id):
        self.access_token = token
        self.artist_id = _id
        self.get_artist_details()

    def get_headers(self):
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        return headers
    
    def get_artist_details(self):
        endpoint = self.base_url + f'{self.artist_id}'
        headers = self.get_headers()

        r = requests.get(endpoint,headers=headers)

        check_status(r, "Failed to load artist details")
        
        data = r.json()

        self.artist_name = data['name']
        self.artist_img = data['images'][0]['url']
        self.followers = data['followers']['total']
        self.popularity = f"{data['popularity']}"


class Track:
    access_token = None
    base_url = 'https://api.spotify.com/v1/tracks/'

    track_id = ''
    track_name = ''
    track_img = ''
    album_name = ''
    spotify_link = ''

    artists = ''

    def __init__(self,token,_id):
        self.access_token = token
        self.track_id = _id
        self.get_track_details()
    
    def get_headers(self):
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        return headers

    def get_track_details(self):
        endpoint = self.base_url + f'{self.track_id}'
        headers = self.get_headers()

        r = requests.get(endpoint,headers=headers)

        check_status(r, "Failed to load Track details")
        
        data = r.json()

        self.track_name = data['name']
        self.track_img = data['album']['images'][0]['url']
        self.album_name = data['album']['name']
        self.spotify_link = data['external_urls']['spotify']

        # self.artists = [i['name'] for i in data['artists']]

        for i in data['artists']:
            if data['artists'].index(i):
                self.artists += ', '
            self.artists += i['name']


class Playlist:
    access_token = None
    base_url = 'https://api.spotify.com/v1/playlists/'
    
    playlist_id = ''
    playlist_name = ''
    playlist_img = ''
    playlist_author = ''
    playlist_desc = ''
    playlist_followers = ''

    tracks_count = ''
    tracks = []

    def __init__(self,token,_id):
        self.access_token = token
        self.playlist_id = _id
        self.get_playlist_details()
    
    def get_headers(self):
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        return headers

    def get_playlist_details(self):
        endpoint = self.base_url + f'{self.playlist_id}'
        headers = self.get_headers()

        r = requests.get(endpoint, headers=headers)

        check_status(r, "Failed to load Playlist details")
        
        data = r.json()

        self.playlist_name = data['name']
        self.playlist_img = data['images'][0]['url']
        self.playlist_author = data['owner']['display_name']
        self.playlist_desc = data['description']
        self.playlist_followers = data['followers']['total']
        self.tracks_count = data['tracks']['total']

        for item in data['tracks']['items']:
            track = {}
            track['id'] = item['track']['id']
            track['name'] = item['track']['name']
            track['img'] = item['track']['album']['images'][0]['url']
            track['album_name'] = item['track']['album']['name']
            track['time'] = mstosec(item['track']['duration_ms'])
            track['artists'] = ''

            for i in item['track']['artists']:
                if item['track']['artists'].index(i):
                    track['artists'] += ', '
                track['artists'] += i['name']
            
            self.tracks.append(track)


class Browse:
    access_token = None

    new_release = []
    featured_Playlist = []
    f_msg = ''

    base_url = 'https://api.spotify.com/v1/browse/'

    def __init__(self,token):
        self.access_token = token
        self.get_new_release()
        self.get_featured_playlist()

    def get_headers(self):
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        return headers

    def browse(self,_type):
        endpoint = f"{self.base_url}{_type}?country=IN&limit=10"
        print(endpoint)
        headers = self.get_headers()

        r = requests.get(endpoint, headers=headers)

        check_status(r, "Failed to load new release details")
        
        return r.json()

    def get_new_release(self):
        data = self.browse('new-releases')['albums']['items']

        for item in data:
            album ={}
            album['img'] = item['images'][0]['url']
            album['name'] = item['name']
            album['link'] = item['external_urls']['spotify']

            self.new_release.append(album)
    
    def get_featured_playlist(self):
        data = self.browse('featured-playlists')

        self.f_msg = data['message']

        for item in data['playlists']['items']:
            playlist = {}
            playlist['img'] = item['images'][0]['url']
            playlist['name'] = item['name']
            playlist['id'] = item['id']

            self.featured_Playlist.append(playlist)


class Search:
    access_token = None
    result = []

    def __init__(self,token,query):
        self.access_token = token
        self.base_url = f"https://api.spotify.com/v1/search?query={query}&type=track&limit=5"
        self.search_res()


    def get_headers(self):
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        return headers

    def search_res(self):
        headers = self.get_headers()
        r = requests.get(self.base_url, headers=headers)

        check_status(r, "Failed to search results")

        data = r.json()['tracks']['items']

        for item in data:
            track_data = {}
            track_data['id'] = item['id']
            track_data['name'] = item['name']
            track_data['artists'] = ''

            for i in item['artists']:
                if item['artists'].index(i):
                    track_data['artists'] += ', '
                track_data['artists'] += i['name'] 

            track_data['album'] = item['album']['name']
            track_data['img'] = item['album']['images'][0]['url']

            track_data['time'] = mstosec(item['duration_ms'])
            self.result.append(track_data)


