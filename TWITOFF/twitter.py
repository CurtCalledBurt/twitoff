"""
Going to retrieve tweets, embeddings,
and save them into a database
"""

import basilica
import tweepy
from decouple import config
from .models import DB, Tweet, User

TWITTER_AUTH = tweepy.OAuthHandler(config('TWITTER_CONSUMER_KEY'),
                                   config('TWITTER_CONSUMER_KEY_SECRET'))
TWITTER_AUTH.set_access_token(config('TWITTER_ACCESS_TOKEN'),
                              config('TWITTER_ACCESS_TOKEN_SECRET'))
TWITTER = tweepy.API(TWITTER_AUTH)
BASILICA = basilica.Connection(config('BASILICA_KEY'))


# additional functions
def add_or_update_user(username):
    """ Add or update a user and their tweets, else error """
    try:
        twitter_user = TWITTER.get_user(username)
        db_user = (
            User.query.get(twitter_user.id) or
            User(id=twitter_user.id, name=username)
            )
        DB.session.add(db_user)
        tweets = twitter_user.timeline(count=200,
                                       exclude_replies=True,
                                       include_rts=False,
                                       tweet_mode='extended',
                                       since_id=db_user.newest_tweet_id)
        if tweets:
            db_user.newest_tweet_id = tweets[0].id
        for tweet in tweets:
            # calculate embedding on the full tweet
            embedding = BASILICA.embed_sentence(tweet.full_text,
                                                model='twitter')
            db_tweet = Tweet(id=tweet.id,
                             text=tweet.full_text[:300],
                             embedding=embedding)
            db_user.tweets.append(db_tweet)
            DB.session.add(db_tweet)
    except Exception as e:
        print(f'Error processing {username}: {e}')
        raise e
    else:
        DB.session.commit()
    # return None


def delete_create_new_db():
    DB.drop_all()
    DB.create_all()
    return None


def add_user_to_db(username: str, num_of_tweets: int):
    """ Takes a twitter username and an integer and will add the user and
    that many of the inputted user's tweets into the database """

    # finds the user with the chosen name
    twitter_user = TWITTER.get_user(username)
    # gets the inputted number of tweets from the selected user
    tweets = twitter_user.timeline(count=num_of_tweets,
                                   exclude_replies=True,
                                   include_rts=False,
                                   tweet_mode='extended')
    # creates the User class object to inputted into the database
    db_user = User(id=twitter_user.id,
                   name=twitter_user.screen_name,
                   newest_tweet_id=tweets[0].id)
    # creates the Tweet class object for each tweet of the user and
    # adds them to the database
    for tweet in tweets:
        embedding = BASILICA.embed_sentence(tweet.full_text, model='twitter')
        db_tweet = Tweet(id=tweet.id,
                         text=tweet.full_text[:500],
                         embedding=embedding)
        DB.session.add(db_tweet)
        db_user.tweets.append(db_tweet)
    # adds the user to the database
    DB.session.add(db_user)
    # saves the changes made to the database
    DB.session.commit()

    return None
