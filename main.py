# all the imports
import os
import sqlite3
from flask import Flask, request, session, g, jsonify, redirect, url_for, abort, \
     render_template, flash

import tweepy

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'pv.db'),
    SECRET_KEY='thisissecretkey',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    """Opens a new database connection if there is none yet for
    the current application context"""
    if not hasattr(g,'sqlite_db'):
        g.sqlite_db=connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g,'sqlite_db'):
        g.sqlite_db.close()

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    init_db()
    print('initialized the database')


@app.route('/')
def show_entries():
    #db = get_db()
    #cur = db.execute('select title, text from entries order by id desc')
    #entries = cur.fetchall()
    tweets = configureTweepy()
    return render_template('index.html',entries=tweets)

@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('insert into entries(title, text) values(?,?)',
    [request.form['title'], request.form['text']])
    db.commit()
    flash('new entry was successfully posted')
    return redirect(url_for('show_entries'))


@app.route('/search', methods=['POST'])
def search():
    searchTxt = request.form['text']
    if searchTxt or searchTxt.strip():
        tweets = api.search(q=searchTxt, count=500, show_user=False, rpp=500, geocode='38.899722,-77.048363,500mi')
        return jsonify({'result': tweets})
    else:
        return jsonify({'result':'invalid keyword sent'})


def searchUsr():
    searchTxt = request.form['text']


def configureTweepy():
    # Consumer keys and access tokens, used for OAuth
    consumer_key = 'goGU9scB0gxJzyeghKawCa5zM'
    consumer_secret = 'aj8fQJfJC6F8SpWJAExGSBvaobeVfxSUAuZn3tzEQEUgZc3giw'
    access_token = '44778234-4mv7600AN7TdnckWp5VVTwTQ9qsa7f9s2gx5Gr5GV'
    access_token_secret = 'bTYo0l4MIKDQgYqQJlGiqSfcLyxkZbVOI93gMEB5iGJb9'

    # OAuth process, using the keys and tokens
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    # Creation of the actual interface, using authentication
    api = tweepy.API(auth)

    public_tweets = api.home_timeline()
    return public_tweets

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))
