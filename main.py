from flask import Flask, request, redirect, url_for, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from helpers import *
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

# Set secret key, otherwise WTF form doesn't work
SECRET_KEY = os.environ.get('SECRET_KEY')

app = Flask(__name__)
executor = ThreadPoolExecutor(max_workers=1)  # Limit the number of concurrent tasks

# Connect to Database
# Struggle with home directory for DB
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL',  'sqlite:///' + os.path.join(basedir, 'ArtistScore.db'))
if app.config['SQLALCHEMY_DATABASE_URI'].startswith('postgres://'):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = SECRET_KEY
app.app_context()
db = SQLAlchemy(app)
migrate = Migrate(app, db)
Bootstrap(app)


# score table configuration
class ArtistScoreDB(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1000), nullable=False)
    language = db.Column(db.String(1000), nullable=False)
    score = db.Column(db.Integer, nullable=True)


# WTF form
class ArtistScoreForm(FlaskForm):
    name = StringField(label='Artist', validators=[DataRequired()])
    submit = SubmitField(label='Submit')


def launch_calculation_and_store_to_db(artist_name, max_songs=None):
    """
    Launch score calculation and then store it to DB
    """

    # Update data in db with new artist and sero score to avoid several searches for the same artist in parallel
    new_artist = ArtistScoreDB(
        name=artist_name,
        language='TBD',
        score=0,
    )

    # Push an application context to write new entry to db
    with app.app_context():
        db.session.add(new_artist)
        db.session.commit()

    # Calculate score
    score = get_artist_score(artist_name, max_songs)

    # Update data in db with calculated score
    with app.app_context():
        try:

            # If score is not 0 then store to DB
            if score['score'] != 0:
                new_artist.score = int(score['score'])
                new_artist.language = str(score['languages'])
                db.session.merge(new_artist)  # Optional, helps ensure the session is aware
                db.session.commit()

            # If score is 0 then delete preliminary entry from DB
            else:
                db.session.delete(new_artist)
                db.session.commit()
        except Exception as e:
            print(e)
            db.session.delete(new_artist)
            db.session.commit()


# Root route
@app.route('/', methods=['GET', 'POST'])
def home():

    # Get data from DB
    artist_score_list_raw = db.session.query(ArtistScoreDB).order_by(ArtistScoreDB.score.desc()).all()

    # Create list of artist and score
    artist_score_list = [
        {
            'id': artist.id,
            'name': artist.name,
            'language': artist.language,
            'score': artist.score,
            'position': position
        }
        for position, artist in enumerate(artist_score_list_raw)
    ]

    # Stats if db has data
    if artist_score_list:
        winner = max(artist_score_list, key=lambda x:x['score'])
        loser = min(artist_score_list, key=lambda x:x['score'])
        average_score = int(sum(d['score'] for d in artist_score_list) / len(artist_score_list))

        # Calculate histogram
        score_frequency, bin_edges = np.histogram([artist['score'] for artist in artist_score_list],
                                                  bins=max(10, len(artist_score_list) // 10))
        score_frequency = score_frequency.tolist()

        # Convert bin_edges to string labels for each bin
        bin_labels = [f"{bin_edges[i]:.2f} - {bin_edges[i+1]:.2f}" for i in range(len(bin_edges)-1)]

    # No stats if db doesn't have data yet
    else:
        winner = loser = {
            'name': 'None',
            'score': 'None'
        }
        average_score = 'None'
        score_frequency = []
        bin_labels = []

    # WTF form
    artist_score_form = ArtistScoreForm()

    # Get message
    message = request.args.get('message', '')

    # If form is submitted
    if artist_score_form.validate_on_submit():

        # Check if artist is not already on db
        if artist_score_form.name.data not in [artist['name'] for artist in artist_score_list]:

            # If not just couple of songs then run the score calculation in background
            future = executor.submit(launch_calculation_and_store_to_db,
                                     artist_score_form.name.data,
                                     100)

            # Prepare the message
            message = f'Processing {artist_score_form.name.data}..'

        # If artist is in db
        else:

            # Prepare the message
            message = f'{artist_score_form.name.data} is already in database'

        # Clear the form
        artist_score_form.name.data = ''

        # Redirect to a new page (could be the same page)
        return redirect(url_for('home', message=message))

    # Render index.html with data from DB
    return render_template('index.html',
                           artist_score_list=artist_score_list,
                           form=artist_score_form,
                           winner=winner,
                           loser=loser,
                           average_score=average_score,
                           score_frequency=score_frequency,
                           bin_labels=bin_labels,
                           message=message)


@app.route('/drop_db')
def drop_db():
    # Handle possible errors with try-except
    try:
        # Delete all entries from DB
        db.session.query(ArtistScoreDB).delete()
        db.session.commit()
        return jsonify({'message': 'Database successfully cleared'}), 200
    # If problems then it's not good
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/append_db', methods=['POST'])
def append_db():

    # Get data
    data = request.json

    # Try to get artists data from JSON
    try:

        # Add all entries to DB
        for entry in data:
            new_artist = ArtistScoreDB(
                name=entry['name'],
                language=entry['language'],
                score=entry['score'],
            )
            db.session.add(new_artist)
        db.session.commit()

        # Return GOOD JOB message
        return jsonify({'message': 'Data added successfully'}), 200

    # If problems then let the remote user know
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# @app.route('/upload_db', methods=['GET', 'POST'])
# def upload_db():
#     artist_score_list_raw = db.session.query(ArtistScoreDB).order_by(ArtistScoreDB.score.desc()).all()
#
#     # Create list of artist and score
#     artist_score_list = [
#         {
#             'name': artist.name,
#             'language': artist.language,
#             'score': artist.score,
#         }
#         for artist in artist_score_list_raw
#     ]
#
#     data = []
#
#     for artist in artist_score_list:
#         data.append({
#                 "name": artist['name'],
#                 "language": artist['language'],
#                 "score": artist['score']
#             })
#
#     response = requests.post('http://www.morze.ch/append_db', json=data)
#     print(response.status_code)
#     return redirect(url_for('home', message='DB uploaded'))


if __name__ == '__main__':
    app.run()

