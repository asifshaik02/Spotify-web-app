from flask import Flask, render_template, redirect, request
from dotenv import load_dotenv
from SpotifyApp import *

load_dotenv()

app = Flask(__name__)


client = None
user = None


@app.route('/')
def main():
    client = None
    return render_template('login.html', h="Spotify Web App")


@app.route('/login')
def login():
    url = SpotifyUserAuth().user_auth()
    return redirect(url)

@app.route('/logout')
def logout():

    client = None
    return redirect('/')


@app.route('/callback')
def callback():

    if request.args.get('code'):
        code = request.args.get('code')

        global client
        client = SpotifyClientAuth(code)

        if not client.client_auth():
            return redirect('/')

        global user
        user = client.get_user()

        return redirect('/home')
    else:
        return redirect('/')

    

@app.route('/home')
def home():

    try:
        h = client.get_home()
    except Exception:
        return render_template('login.html',h="Uh-Oh!! Login Again")

    return render_template('home.html',h = h)


@app.route('/search')
def search():
    if request.args.get('q'):
        return search_res(request.args.get('q'))
    return render_template('search.html',s='s')


@app.route('/search/<q>')
def search_res(q):

    try:
        s = client.search(q)
    except Exception:
        return render_template('login.html',h="Uh-Oh!! Login Again")

    return render_template('search.html',s=s)



@app.route('/user-history')
def history():

    try:
        h = user.recently_played
    except Exception:
        return render_template('login.html',h="Uh-Oh!! Login Again")

    return render_template('user-history.html',h=h)


@app.route('/user-playlist')
def user_playlist():

    try:
        p = user.playlist  
    except Exception:
        return render_template('login.html',h="Uh-Oh!! Login Again")
    
    return render_template('user-playlist.html', p=p)


@app.route('/user-profile')
def profile():    
    u = user
    return render_template('user-profile.html',u=u)


@app.route('/track/<t_id>')
def track(t_id):

    try:
        t = client.get_track(t_id)
    except Exception:
        return render_template('login.html',h="Uh-Oh!! Login Again")

    return render_template('track.html',t=t)

@app.route('/artist/<a_id>')
def artist(a_id):

    try:
        a = client.get_artist(a_id)
    except Exception:
        return render_template('login.html',h="Uh-Oh!! Login Again")

    return render_template('artist.html', a=a)

@app.route('/playlist/<p_id>')
def playlsit(p_id):

    try:
        p = client.get_playlist(p_id)
    except Exception:
        return render_template('login.html',h="Uh-Oh!! Login Again")

    return render_template('playlist.html',p=p)




if __name__ == '__main__':
    app.run(debug=True)