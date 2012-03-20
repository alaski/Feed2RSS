from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response
from pyramid.view import view_config

from .models import (
    DBSession,
    User,
    )

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
    user = api.me()
    #oauth_token = auth.access_token.key
    #oauth_token_secret = auth.access_token.secret
    print user.id
    print user.screen_name

@view_config(route_name='home', renderer='templates/home.pt')
def home(request):
    return {'project': 'Feed2RSS'}


# vim:et:ts=4:sw=4:sts=4
