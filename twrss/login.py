from flaskext.login import LoginManager
from twrss import app

login_manager = LoginManager()
login_manager.setup_app(app)

@login_manager

# vim:et:ts=4:sw=4:sts=4
