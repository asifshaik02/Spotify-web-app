# The movie database

using [Spotify](https://www.spotify.com/)'s api made this movie database project.  

[Live demo](https://spotifywebapp0.herokuapp.com/)

## setting up

**clone this repo:**

`git clone https://github.com/asifshaik02/spotify-web-app.git`

`cd spotify-web-app`

**creating virual environment:**

`virtualenv env`

for linux:
`source env/bin/activate`

for windows:
`\env\Scripts\activate.bat`

**Install requirements:**

`pip install -r requirements.txt`

**Api key:**

create an account in [spotify](https://www.spotify.com/) and get an API key.

create a file named `.env` in that file enter:
`CLIENT_ID = <your_client_id>`
`CLIENT_SECRECT = <your_client_secret>`

**Run on local server:**

`python app.py`