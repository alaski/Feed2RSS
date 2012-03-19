from fabric.api import local
from fabric.api import task
from fabric.context_managers import prefix
from contextlib import contextmanager
import os
import sys

@contextmanager
def include_cwd(): 
    if os.getcwd() in sys.path or '' in sys.path:
        yield
    else:
        prev_sys_path = list(sys.path)
        sys.path.insert(0, os.path.abspath(os.getcwd()))
        try:
            yield
        finally:
            for item in list(sys.path):
                if item not in prev_sys_path:
                    sys.path.remove(item)

@task
def test():
    test_command = 'nosetests -v'
    if 'VIRTUAL_ENV' in os.environ:
        activate_command = '. {0}'.format(os.path.join(os.environ['VIRTUAL_ENV'], 'bin/activate'))
        with prefix(activate_command):
                local(test_command)
    else:
        local(test_command)

@task
def db_init():
    with include_cwd():
        from feed2rss.models import db
        db.drop_all()
        db.create_all()


# vim:et:ts=4:sw=4:sts=4
