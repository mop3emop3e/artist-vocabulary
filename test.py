from helpers import *
from main import *
import csv
import pandas as pd
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Maximum number opf threads
MAX_THREADS = 10

csv_file_path = './best_selling_artists.csv'
data = pd.read_csv(csv_file_path)

start_time = time.perf_counter()

with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
    # Create a dictionary to hold future to row mapping
    future_to_artist = {executor.submit(launch_calculation_and_store_to_db, row['Artist'], 100): row for index, row in data.iterrows()}

    for future in as_completed(future_to_artist):
        artist = future_to_artist[future]
        try:
            future.result()  # This would be useful if the function returns something or to catch exceptions
        except Exception as e:
            print(f'{artist["Artist"]} generated an exception: {e}')

duration = time.perf_counter() - start_time
print(f'{duration} sec.')




# ==== APPROXIMATION OF LEMMAS CURVE =====



# import numpy as np
# from scipy.optimize import curve_fit
# import matplotlib.pyplot as plt
#
#
# with open('./Eminem_data.txt', 'r', encoding='utf-8') as file:
#     raw_data = file.read()
#
# less_raw_data = raw_data.split('\n')
# even_less_raw_data = [line.split(',')[-1].strip(' ') for line in less_raw_data]
# cooked_data = [int(value) for value in even_less_raw_data if value != '']
# print(cooked_data)
#
# # Example data: x_values as the number of songs analyzed, y_values as the cumulative number of unique lemmas
# x_values = list(range(0, len(cooked_data)))
# y_values = cooked_data
#
#
# # Define the logistic growth model
# def logistic_growth(x, L_max, k, x_0):
#     return L_max / (1 + np.exp(-k * (x - x_0)))
#
#
# # Fit the model to the data
# popt, pcov = curve_fit(logistic_growth, x_values, y_values, maxfev=10000)
#
# # Extract the best-fitting parameters
# L_max, k, x_0 = popt
#
# print(f"L_max: {L_max}, k: {k}, x_0: {x_0}")
#
# # Optional: Plot the data and the fitted curve
# x_fit = np.linspace(min(x_values), max(x_values), 100)
# y_fit = logistic_growth(x_fit, *popt)
#
# plt.scatter(x_values, y_values, label='Data')
# plt.plot(x_fit, y_fit, '-r', label='Fitted curve')
# plt.legend()
# plt.xlabel('Number of Songs Analyzed')
# plt.ylabel('Cumulative Number of Unique Lemmas')
# plt.show()


# ===== UPLOAD THE DB =====

# Get data from DB
with app.app_context():
    artist_score_list_raw = db.session.query(ArtistScoreDB).order_by(ArtistScoreDB.score.desc()).all()

# Create list of artist and score
artist_score_list = [
    {
        'name': artist.name,
        'languages': artist.language,
        'score': artist.score,
    }
    for artist in artist_score_list_raw
]

data = {}

for artist in artist_score_list:
    data.update({
        artist: {
            'name': artist['name'],
            'languages': artist['languages'],
            'score': artist['score']
        }
    })

print(data)

# response = request.post('http://morze.ch/append_db', params=data)
