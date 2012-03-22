import datetime

from pyramid.security import (
    Allow,
    Everyone,
    )

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

from sqlalchemy.orm.exc import NoResultFound

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    screen_name = Column(String(255), unique=True)
    user_id = Column(Integer, unique=True)
    oauth_token = Column(String(255))
    oauth_token_secret = Column(String(255))
    signup_date = Column(DateTime, default=datetime.datetime.now)
    last_login = Column(DateTime)

    def __init__(self,
                 screen_name = '',
                 user_id = -1,
                 oauth_token = '',
                 oauth_token_secret = ''
                 ):
        self.screen_name = screen_name
        self.user_id = user_id
        self.oauth_token = oauth_token
        self.oauth_token_secret = oauth_token_secret

    @classmethod
    def get_by_screen_name(cls, screen_name):
        try:
            user = DBSession.query(cls).filter_by(screen_name=screen_name).one()
        except NoResultFound:
            return None
        return user

    def __str__(self):
        return ('<User screen_name: {screen_name} '
        'user_id: {user_id} '
        'created: {created} '
        'last_login: {last_login}>').format(
            screen_name = self.screen_name,
            user_id =  self.user_id,
            created = self.signup_date,
            last_login = self.last_login
            )


class RootFactory(object):
    __acl__ = [ (Allow, Everyone, 'view') ]

    def __init__(self, request):
        pass

# vim:et:ts=4:sw=4:sts=4