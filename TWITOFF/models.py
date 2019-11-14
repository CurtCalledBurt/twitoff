""" Database models """
from flask_sqlalchemy import SQLAlchemy

# import database, capital for global scope
DB = SQLAlchemy()


class User(DB.Model):
    """Twitter users that we analyze"""
    id = DB.Column(DB.Integer, primary_key=True)
    name = DB.Column(DB.String(15), nullable=False)
    newest_tweet_id = DB.Column(DB.BigInteger)

    def __repr__(self):
        return f'<User {self.name}>'


class Tweet(DB.Model):
    """The user's tweets from twitter"""
    id = DB.Column(DB.BigInteger, primary_key=True)
    text = DB.Column(DB.Unicode(500))
    user_id = DB.Column(DB.BigInteger, DB.ForeignKey('user.id'), nullable=False)
    user = DB.relationship('User', backref=DB.backref('tweets', lazy=True))

    embedding = DB.Column(DB.PickleType, nullable=False)

    # nicer formatting
    def __repr__(self):
        return f'<Tweet {self.text}>'


# while within the flask shell
# from TWITOFF.models import *
# DB.create_all()
# u1=User(name='austen')
# t1=Tweet(text='wheeeee!!!!')
# DB.session.add(u1)
# DB.session.add(t1)
# DB.session.commit()
