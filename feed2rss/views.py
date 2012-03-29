import datetime
from pyramid.httpexceptions import (
    HTTPFound,
    HTTPForbidden,
    HTTPNotFound,
    )

from pyramid.response import Response

from pyramid.security import (
    remember,
    forget,
    authenticated_userid,
    )

from pyramid.view import (
    view_config,
    #forbidden_view_config,
    )

from .models import (
    DBSession,
    Feed,
    User,
    )

import PyRSS2Gen
import tweepy

@view_config(route_name='twitter_login')
def twitter_login(request):
    settings = request.registry.settings
    auth = tweepy.OAuthHandler(
            settings['twconsumer_key'],
            settings['twconsumer_secret'],
            request.route_url('twitter_authenticated')
            )
    try:
        redirect_url = auth.get_authorization_url(signin_with_twitter=True)
    except tweepy.TweepError, e:
        print 'Failed to get request token: {0}'.format(e)
    session = request.session
    session['request_token'] = (
            auth.request_token.key,
            auth.request_token.secret
            )
    session.changed()
    return HTTPFound(location=redirect_url)

@view_config(route_name='twitter_authenticated')
def twitter_authenticated(request):
    verifier = request.GET.getone('oauth_verifier')
    settings = request.registry.settings
    auth = tweepy.OAuthHandler(
            settings['twconsumer_key'],
            settings['twconsumer_secret']
            )
    session = request.session
    token = session.get('request_token')
    if 'request_token' in session:
        del session['request_token']
    auth.set_request_token(token[0], token[1])

    try:
        auth.get_access_token(verifier)
    except tweepy.TweepError:
        print 'Failed to get access token'
    
    api = tweepy.API(auth)
    tw_user = api.me()
    oauth_token = auth.access_token.key
    oauth_token_secret = auth.access_token.secret
    user = User.get_by_screen_name(tw_user.screen_name)
    if user is None:
        user = User(
                tw_user.screen_name,
                tw_user.id,
                oauth_token,
                oauth_token_secret
                )
        DBSession.add(user)
        user = User.get_by_screen_name(tw_user.screen_name)
        favorites_feed = Feed(user.id, 'favorites', 'favorites', False)
        timeline_feed = Feed(user.id, 'timeline', 'timeline', False)
        DBSession.add(favorites_feed)
        DBSession.add(timeline_feed)
    else:
        if user.oauth_token != oauth_token:
            user.oauth_token = oauth_token
        if user.oauth_token_secret != oauth_token_secret:
            user.oauth_token_secret = oauth_token_secret

    user.last_login = datetime.datetime.now()
    DBSession.add(user)
    user_home = request.route_url('user_home', user=tw_user.screen_name)
    headers = remember(request, tw_user.screen_name)
    return HTTPFound(location = user_home, headers = headers)

@view_config(route_name='user_home', renderer='templates/user_home.pt')
def user_home(request):
    user_name = request.matchdict['user']
    logged_in = authenticated_userid(request)
    if user_name != logged_in:
        return HTTPForbidden()
    
    user = User.get_by_screen_name(user_name)
    feeds_cursor = Feed.get_by_userid(user.id)
    feeds = []
    if feeds_cursor is not None:
        for feed in feeds_cursor:
            feed_url = request.route_url(
                    'view_feed',
                    user = user_name,
                    feedname = feed.name,
                    )
            feeds.append({
                        'type': feed.source,
                        'url': feed_url,
                        'active': feed.active
                        })

    return {'screen_name': user_name,
            'feeds': feeds,}

@view_config(route_name='view_feed')
def view_feed(request):
    user = User.get_by_screen_name(request.matchdict['user'])
    feed = Feed.get_by_id_and_name(user.id, request.matchdict['feedname'])
    if feed is None:
        return HTTPNotFound()

    tweets_db = request.mongo_db.tweets
    tweets_cursor = tweets_db.find(
            {'rss_user': user.screen_name, 'feedname': feed.name}
            )
    rss_tweets = []
    for tweet in tweets_cursor:
        rss_tweets.append(
                PyRSS2Gen.RSSItem(
                    title = tweet['title'],
                    author = tweet['author'],
                    link = tweet['link'],
                    description = tweet['description'],
                    pubDate = tweet['pubDate'],
                    )
                )
    rss = PyRSS2Gen.RSS2(
            title = 'Feed2RSS',
            link = request.route_url(
                'view_feed',
                user = request.matchdict['user'],
                feedname = request.matchdict['feedname'],
                ),
            description = 'RSS feed of tweets with links',
            lastBuildDate = datetime.datetime.now(),
            items = rss_tweets,
            )

    return Response(rss.to_xml(), content_type='text/xml')


@view_config(route_name='create_feed', request_method='POST')
def create_feed(request):
    user_name = request.matchdict['user']
    logged_in = authenticated_userid(request)
    if user_name != logged_in:
        return HTTPForbidden()

    form_data = request.POST

    user = User.get_by_screen_name(user_name)
    feed = Feed(user.id, form_data['name'], form_data['source'])
    DBSession.add(feed)
    #settings = request.registry.settings
    #auth = tweepy.OAuthHandler(
    #        settings['twconsumer_key'],
    #        settings['twconsumer_secret']
    #        )
    #auth.set_access_token(user.oauth_token, user.oauth_token_secret)
    #api = tweepy.API(auth)
    #api.favorites()
    return Response()

@view_config(route_name='home', renderer='templates/home.pt')
def home(request):
    return {
            'project': 'Feed2RSS',
            'logged_in': authenticated_userid(request),
            }

@view_config(route_name='logout')
def logout(request):
    headers = forget(request)
    home = request.route_url('home')
    return HTTPFound(location = home, headers = headers)

# vim:et:ts=4:sw=4:sts=4
