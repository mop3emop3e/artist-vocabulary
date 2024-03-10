from helpers import *
from main import *
import csv
import pandas as pd
import re


csv_file_path = './best_selling_artists.csv'

data = pd.read_csv(csv_file_path)

for index, row in data.iterrows():
    print(row['Artist'], ' ', row['Country'])
    if row['Country'] == 'France':
        launch_calculation_and_store_to_db(row['Artist'], 'fr', 10000)
    elif row['Country'] == 'Germany':
        launch_calculation_and_store_to_db(row['Artist'], 'de', 10000)
    elif row['Country'] == 'Italy':
        launch_calculation_and_store_to_db(row['Artist'], 'it', 10000)
    elif row['Country'] == 'Russia':
        launch_calculation_and_store_to_db(row['Artist'], 'ru', 10000)
    else:
        launch_calculation_and_store_to_db(row['Artist'], 'en', 10000)


# csv_file_path = './best_selling_artists.csv'
#
# data = pd.read_csv(csv_file_path)
#
# for index, row in data.iterrows():
#
#     print(row['Artist'], ' - ', row['Country'])
#
#     if row['Country'] in ['United Kingdom', 'United States', 'Canada', 'Australia', 'Jamaica', 'Barbados']:
#
#         try:
#             with open(f"./{row['Artist'].replace('/', ' ')}_temp_lyrics.txt", 'r', encoding='utf-8') as file:
#                 temp = file.read()
#
#             # Regular expression to match text within square brackets
#             temp = re.sub(r'\[.*?\]', '', temp)
#
#             # Regular expression to remove Cyrillic characters but keep Latin characters, including those with diacritics
#             temp = re.sub(r'[А-Яа-яЁё]+', ' ', temp)
#
#             # Load the model for English language
#             nlp_en = spacy.load("en_core_web_sm")
#             nlp_en.max_length = 5000000
#             doc = nlp_en(temp)
#
#             lemmas = [token.lemma_ for token in doc if token.is_alpha]
#             unique_lemmas = set(lemmas)
#
#             # Update data in db
#             new_artist = ArtistScoreDB(
#                 name=row['Artist'],
#                 language='en',
#                 score=len(unique_lemmas),
#             )
#
#             # Push an application context to write new entry to db
#             with app.app_context():
#                 db.session.add(new_artist)
#                 db.session.commit()
#
#         except Exception as e:
#             print(e)

