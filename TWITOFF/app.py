from decouple import config
from flask import Flask, render_template, request
from .models import DB, User
from .twitter import add_or_update_user
from .predict import predict_user
from dotenv import load_dotenv
load_dotenv()


# now we make a app factory

def create_app():
    app = Flask(__name__)

    # add our config
    app.config['SQLALCHEMY_DATABASE_URI'] = config('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # now have the database know about the app
    DB.init_app(app)

    @app.route('/')
    def root():
        users = User.query.all()
        return render_template('base.html',
                               title='Home',
                               users=users)

    @app.route('/reset')
    def reset():
        DB.drop_all()
        DB.create_all()
        return render_template('base_html',
                               title='Reset',
                               users=[])

    # route to add users or get users
    @app.route('/user', methods=['POST'])
    @app.route('/user/<name>', methods=['GET'])
    def user(name=None, message=' '):
        name = name or request.values['user_name']
        try:
            if request.method == 'POST':
                add_or_update_user(name)
                message = f"User {name} successfully added!"
            tweets = User.query.filter(User.name == name).one().tweets

        except Exception as e:
            message = f"Error adding {name}: {e}"
            tweets = []

        return render_template('user.html',
                               title=name,
                               tweets=tweets,
                               message=message)

    # adding a route for prediction
    @app.route('/compare', methods=['POST'])
    def compare(message=' '):
        user1, user2 = sorted([request.values['user1'],
                               request.values['user2']])
        if user1 == user2:
            message = """ What point is there comparing a user to
                        themselves, you silly person? """
        else:
            prediction = predict_user(user1,
                                      user2,
                                      request.values['tweet_text'])

            text = request.values['tweet_text']
            user_winner = user1 if prediction else user2
            user_loser = user2 if prediction else user1

            message = f""""{text}" is more likely to be said by
                        {user_winner} than {user_loser}"""
        return render_template('prediction.html',
                               title='Prediction',
                               message=message)

    return app
