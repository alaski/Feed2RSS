import datetime
from flaskext import login
from flaskext.sqlalchemy import SQLAlchemy
from twrss import app

db = SQLAlchemy(app)

class User(db.Model, login.UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    screen_name = db.Column(db.String(255), unique=True)
    user_id = db.Column(db.Integer, unique=True)
    oauth_token = db.Column(db.String(255))
    oauth_token_secret = db.Column(db.String(255))
    signup_date = db.Column(db.DateTime, default=datetime.datetime.now)

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

    def __str__(self):
        return ('<User screen_name: {screen_name} '
        'user_id: {user_id} '
        'created: {created} '
        'oauth_token: {oauth_token}>').format(
            screen_name = self.screen_name,
            user_id =  self.user_id,
            created = self.created,
            oauth_token = self.oauth_token
            )

# vim:et:ts=4:sw=4:sts=4
