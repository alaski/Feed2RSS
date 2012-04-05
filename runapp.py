import os
import signal

from paste.deploy import loadapp
from waitress import serve

def graceful_shutdown(signum, frame):
    print 'Shutdown called with signal {0}'.format(signum)
    exit()

signal.signal(signal.SIGTERM, graceful_shutdown)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app = loadapp('config:production.ini', relative_to='.')

    serve(app, host='0.0.0.0', port=port)

# vim:et:ts=4:sw=4:sts=4
