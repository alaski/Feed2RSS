from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from sqlalchemy import engine_from_config

from .models import DBSession

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    session_factory = UnencryptedCookieSessionFactoryConfig('topsecret')
    authn_policy = AuthTktAuthenticationPolicy('topsecret2')
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

