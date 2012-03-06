from flask import Flask

app = Flask(__name__)
app.config.from_pyfile('config.ini')

import twrss.views

# vim:et:ts=4:sw=4:sts=4
