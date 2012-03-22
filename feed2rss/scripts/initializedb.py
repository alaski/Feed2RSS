import os
import sys
#import transaction

from sqlalchemy import create_engine

from pyramid.paster import (
    setup_logging,
    )

from ..models import (
    DBSession,
    User,
    Base,
    )

def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd)) 
    sys.exit(1)

def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    database_url = os.environ.get('DATABASE_URL')
    engine = create_engine(database_url, echo=True)
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
    #with transaction.manager:
    #    model = User()
    #    DBSession.add(model)
