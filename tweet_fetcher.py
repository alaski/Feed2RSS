import os
import re
import sys

import pymongo
from sqlalchemy import create_engine
import tweepy

from feed2rss.models import (
    DBSession,
    Feed,
    User,
    )


def main(argv=None):
    if argv is None:
        argv = sys.argv

    link_re = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')

    database_url = os.environ.get('DATABASE_URL')
    engine = create_engine(database_url)
    DBSession.configure(bind=engine)

    mongo_uri = os.environ.get('MONGO_URI')
    mongo_name = os.environ.get('MONGO_NAME')
    mongo_conn = pymongo.Connection(mongo_uri)
    mongo_db = mongo_conn[mongo_name]
    mongo_tweets = mongo_db.tweets

    twconsumer_key = os.environ.get('TWCONSUMER_KEY')
    twconsumer_secret = os.environ.get('TWCONSUMER_SECRET')

    for feed in DBSession.query(Feed):
        user = DBSession.query(User).filter_by(id=feed.user_id).one()
        rss_username = user.screen_name

        auth = tweepy.OAuthHandler(twconsumer_key, twconsumer_secret)
        auth.set_access_token(user.oauth_token, user.oauth_token_secret)
        api = tweepy.API(auth)
        try:
            for tweet in api.favorites():
                tweet_text = unicode(tweet.text).encode('utf-8')
                link_match = link_re.search(tweet_text)
                if link_match is not None:
                    link = unicode(link_match.group(0)).encode('utf-8')
                    tweet_persist = {
                            'rss_user': rss_username,
                            'feedname': feed.name,
                            'tweet_id': tweet.id_str,
                            'title': link,
                            'author': tweet.user.screen_name,
                            'link': link,
                            'description': '{0}'.format(tweet_text),
                            'pubDate': tweet.created_at
                            }
                    mongo_tweets.insert(tweet_persist)
        except tweepy.error.TweepError:
            # Most likely failed auth, needs better handling
            pass
    #db.tweets.ensureIndex({tweet_id:1, rss_user:1, feedname:1},{unique:true})


if __name__ == '__main__':
    sys.exit(main())

# vim:et:ts=4:sw=4:sts=4
