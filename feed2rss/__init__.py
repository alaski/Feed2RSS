import os

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from sqlalchemy import create_engine

from .models import DBSession

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    settings['twconsumer_key'] = os.environ.get('TWCONSUMER_KEY')
    settings['twconsumer_secret'] = os.environ.get('TWCONSUMER_SECRET')
    session_secret = os.environ.get('SESSION_SECRET')
    auth_secret = os.environ.get('AUTH_SECRET')
    database_url = os.environ.get('DATABASE_URL')
    engine = create_engine(database_url)
    DBSession.configure(bind=engine)
    session_factory = UnencryptedCookieSessionFactoryConfig(session_secret)
    authn_policy = AuthTktAuthenticationPolicy(auth_secret)
    authz_policy = ACLAuthorizationPolicy()
    config = Configurator(
            settings=settings,
            session_factory=session_factory,
            root_factory='.models.RootFactory',
            )
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('twitter_login', '/twitter_login')
    config.add_route('twitter_authenticated', '/twitter_authenticated')
    config.add_route('logout', '/logout')
    config.add_route('user_home', '/users/{user}')
    config.scan()
    return config.make_wsgi_app()

