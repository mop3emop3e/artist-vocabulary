from helpers import *
from main import *
import csv
import pandas as pd
import re
import time

# import requests
#
# # Replace this URL with the actual URL where your Flask app is hosted
# url = "http://www.morze.ch/drop_db"
#
# # Sending GET request to the Flask app
# response = requests.get(url)
#
# # Printing the response from the server
# print("Status Code:", response.status_code)
# print("Response:", response.json())


csv_file_path = './best_selling_artists.csv'

data = pd.read_csv(csv_file_path)

thread = []

for index, row in data.iterrows():
    if row['Country'] == 'France':
        thread.append(threading.Thread(target=launch_calculation_and_store_to_db, args=(row['Artist'],
                                                                                        'fr',
                                                                                        100)))
        thread[-1].start()
    elif row['Country'] == 'Germany':
        thread.append(threading.Thread(target=launch_calculation_and_store_to_db, args=(row['Artist'],
                                                                                        'de',
                                                                                        100)))
        thread[-1].start()
    elif row['Country'] == 'Italy':
        thread.append(threading.Thread(target=launch_calculation_and_store_to_db, args=(row['Artist'],
                                                                                        'it',
                                                                                        100)))
        thread[-1].start()
    elif row['Country'] == 'Spain':
        thread.append(threading.Thread(target=launch_calculation_and_store_to_db, args=(row['Artist'],
                                                                                        'es',
                                                                                        100)))
        thread[-1].start()
    elif row['Country'] == 'Russia':
        thread.append(threading.Thread(target=launch_calculation_and_store_to_db, args=(row['Artist'],
                                                                                        'ru',
                                                                                        100)))
        thread[-1].start()
    else:
        thread.append(threading.Thread(target=launch_calculation_and_store_to_db, args=(row['Artist'],
                                                                                        'en',
                                                                                        100)))
        thread[-1].start()

    while len(thread) >= 10:
        print(index)
        for i in range(len(thread)):
            if not thread[i].is_alive():
                thread.pop(i)
                break
        time.sleep(5)

while len(thread) < 0:
    print(len(thread))
    for i in range(len(thread)):
        if not thread[i].is_alive():
            thread.pop(i)
            break
    time.sleep(5)






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

