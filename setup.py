import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid',
    'SQLAlchemy',
    'transaction',
    'pyramid_tm',
    'pyramid_debugtoolbar',
    'zope.sqlalchemy',
    'waitress',
    'psycopg2',
    'pyramid_assetviews',
    'pymongo',
    'PyRSS2Gen',
    'tweepy',
    ]

setup(name='feed2rss',
      version='0.1',
      description='feed2rss',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='feed2rss',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = feed2rss:main
      [console_scripts]
      initialize_feed2rss_db = feed2rss.scripts.initializedb:main
      """,
      )
