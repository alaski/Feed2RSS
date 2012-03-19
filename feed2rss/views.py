from flask import flash
from flask import redirect
from flask import render_template
from flask import url_for
from flaskext.login import current_user
from flaskext.login import login_required
from flaskext.login import login_user
from flaskext.login import logout_user
from flaskext.login import LoginManager
from flaskext.oauth import OAuth
import PyRSS2Gen
import tweepy

from feed2rss import app
from feed2rss import models

import datetime
import re


oauth = OAuth()
twitter = oauth.remote_app('twitter',
        base_url = 'https://api.twitter.com/1/',
        request_token_url = 'https://api.twitter.com/oauth/request_token',
        access_token_url = 'https://api.twitter.com/oauth/access_token',
        authorize_url = 'https://api.twitter.com/oauth/authenticate',
        consumer_key = app.config['TWCONSUMER_KEY'],
        consumer_secret = app.config['TWCONSUMER_SECRET']
)
login_manager = LoginManager()
login_manager.setup_app(app)
login_manager.login_view = 'twitter_authenticated'

@twitter.tokengetter
def get_twitter_token():
    if current_user.is_anonymous():
        return None

    user = models.User.query.filter_by(id=current_user.id).first()
    if user is None:
        return None

    return (user.oauth_token, user.oauth_token_secret)

@login_manager.user_loader
def load_user(user_id):
    return models.User.query.filter_by(id=user_id).first()

@app.route('/twitter_login')
def twitter_login():
    return twitter.authorize(callback = url_for('twitter_authenticated'))

@app.route('/authenticated')
@twitter.authorized_handler
def twitter_authenticated(resp):
    if resp is None:
        flash(u'You denied the request to sign in.')
        return redirect(url_for('home'))

    user = models.User.query.filter_by(screen_name=resp['screen_name']).first()
    if user is None:
        user = models.User(
            screen_name = resp['screen_name'],
            user_id = resp['user_id'],
            oauth_token = resp['oauth_token'],
            oauth_token_secret = resp['oauth_token_secret']
            )

        models.db.session.add(user)
    else:
        if user.oauth_token != resp['oauth_token']:
            user.oauth_token = resp['oauth_token']
        if user.oauth_token_secret != resp['oauth_token_secret']:
            user.oauth_token_secret = resp['oauth_token_secret']

    models.db.session.commit()

    login_user(user, remember=True)
    return redirect(url_for('user_home', user=user.screen_name))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/')
def home():
    if current_user.is_anonymous():
        user = models.User()
    else:
        user = current_user

    return render_template(
            'home.html',
            logged_in = current_user.is_authenticated(),
            user = user
            )

@app.route('/<user>')
@login_required
def user_home(user):
    link_re = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    consumer_key = app.config['TWCONSUMER_KEY']
    consumer_secret = app.config['TWCONSUMER_SECRET']
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    key = current_user.oauth_token
    secret = current_user.oauth_token_secret
    auth.set_access_token(key, secret)
    api = tweepy.API(auth)

    rss_items = []
    for status in api.favorites():
        link = link_re.search(status.text)
        if link is not None:
            rss_items.append(PyRSS2Gen.RSSItem(
                title = unicode(link.group(0)).encode('utf-8'),
                author = status.user.screen_name,
                link = unicode(link.group(0)).encode('utf-8'),
                description = status.text,
                pubDate = status.created_at
                )
            )

    rss = PyRSS2Gen.RSS2(
            title = 'Tweets to RSS',
            link = url_for('home'),
            description = 'Links!',
            lastBuildDate = datetime.datetime.now(),
            items = rss_items
    )

    return rss.to_xml()


# vim:et:ts=4:sw=4:sts=4
