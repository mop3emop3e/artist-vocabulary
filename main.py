from flask import Flask, jsonify, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FieldList, SelectField, FormField
from wtforms.validators import DataRequired, Optional
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from helpers import *
import threading
import numpy as np

# Set secret key, otherwise WTF form doesn't work
SECRET_KEY = os.urandom(32)

app = Flask(__name__)

# Connect to Database
# Struggle with home directory for DB
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL',  'sqlite:///' + os.path.join(basedir, 'ArtistScore.db'))
if app.config['SQLALCHEMY_DATABASE_URI'].startswith('postgres://'):
    app.config['SQLALCHEMY_DATABASE_URI'].replace('postgres://', 'postgresql://', 1)
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
    language = db.Column(db.String(2), nullable=False)
    score = db.Column(db.Integer, nullable=True)


# WTF form
class ArtistScoreForm(FlaskForm):
    name = StringField(label='Artist', validators=[DataRequired()])
    language = SelectField('Language', choices=[('en', 'English'),
                                                ('de', 'German'),
                                                ('fr', 'French'),
                                                ('es', 'Spanish'),
                                                ('it', 'Italian'),
                                                ('ru', 'Russian')])
    submit = SubmitField(label='Submit')


def launch_calculation_and_store_to_db(artist_name, language='en', max_songs=None):
    """
    Launch score calculation and then store it to DB
    """

    # Calculate score
    score = get_artist_score(artist_name, language, max_songs)

    # Update data in db
    new_artist = ArtistScoreDB(
        name=artist_name,
        language=language,
        score=score,
    )

    # Push an application context to write new entry to db
    with app.app_context():
        db.session.add(new_artist)
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
        score_frequency, bin_edges = np.histogram([artist['score'] for artist in artist_score_list], bins=20)
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

    message = ''

    # If form is submitted
    if artist_score_form.validate_on_submit():

        # Check if artist is not already on db
        if artist_score_form.name.data not in [artist['name'] for artist in artist_score_list]:

            # Run the score calculation in background
            thread = threading.Thread(target=launch_calculation_and_store_to_db, args=(artist_score_form.name.data,
                                                                                       artist_score_form.language.data,
                                                                                       10000))
            thread.start()

            # Prepare the message
            message = f'Processing {artist_score_form.name.data}, {artist_score_form.language.data}'

        # If artist is in db
        else:

            # Prepare the message
            message = f'{artist_score_form.name.data} is already in database'

        # Clear the form
        artist_score_form.name.data = ''
        artist_score_form.language.data = 'en'

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


# def check_and_create_db():
#     """
#     Check if DB exists, create it if not
#     """
#
#     # Create an application context
#     with app.app_context():
#
#         # Check if DB file exists
#         if not os.path.exists(os.path.join(basedir, 'ArtistScore.db')):
#
#             # Create DB and tables
#             db.create_all()


# Check if DB exists. Create new one if not
# check_and_create_db()

if __name__ == '__main__':
    app.run(debug=True)
