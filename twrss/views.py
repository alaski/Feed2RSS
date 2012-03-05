from flask import flash
from flask import redirect
from flask import request
from flask import session
from flask import url_for
from flaskext.oauth import OAuth
import PyRSS2Gen
import tweepy
from twss import app

import datetime
import re

link_re = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')

oauth = OAuth()
twitter = oauth.remote_app('twitter',
        base_url = 'https://api.twitter.com/1/',
        request_token_url = 'https://api.twitter.com/oauth/request_token',
        access_token_url = 'https://api.twitter.com/oauth/access_token',
        authorize_url = 'https://api.twitter.com/oauth/authenticate',
        consumer_key = app.config['TWCONSUMER_KEY'],
        consumer_secret = app.config['TWCONSUMER_SECRET']
)

@twitter.tokengetter
def get_twitter_token():
    return session.get('twitter_token')

@app.route('/twrss/login')
def twitter_login():
    return twitter.authorize(callback=url_for('twitter_authenticated'))

@app.route('/twrss/authenticated')
@twitter.authorized_handler
def twitter_authenticated(resp):
    next_url = request.args.get('next') or url_for('index')
    if resp is None:
        flash(u'You denied the request to sign in.')
        return redirect(next_url)

    session['twitter_token'] = (
        resp['oauth_token'],
        resp['oauth_token_secret']
    )
    session['twitter_user'] = resp['screen_name']

    flash(u'You were signed in as {0}'.format(resp['screen_name']))
    return redirect(next_url)

@app.route('/twrss')
def index():
    consumer_token = app.config['TWCONSUMER_TOKEN']
    consumer_secret = app.config['TWCONSUMER_SECRET']
    auth = tweepy.OAuthHandler(consumer_token, consumer_secret)
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
            link = url_for('index'),
            description = 'Links!',
            lastBuildDate = datetime.datetime.now(),
            items = rss_items
    )

    return rss.to_xml()


# vim:et:ts=4:sw=4:sts=4
