from lyricsgenius import Genius
import spacy
import re
import os
from langdetect import detect
import gc
import requests

# Access token for genius.com
CLIENT_ACCESS_TOKEN = os.environ.get('CLIENT_ACCESS_TOKEN')


# def get_artist_score(artist_name, language='en', max_songs=None):
def get_artist_score(artist_name, max_songs=None):

    """
    Get number of unique words used by artists in all songs
    :return: number of all unique words
    """

    # Create Genius object
    genius = Genius(CLIENT_ACCESS_TOKEN,
                    remove_section_headers=True,
                    skip_non_songs=True)

    # Set number of retries
    genius.retries = 20

    # Get artist object by name
    while True:

        # Try until good response
        try:
            artist = genius.search_artist(artist_name,
                                          max_songs=max_songs,
                                          sort='popularity')

            # Get full name
            artist_name = artist.name

            # If some realistic number of songs exist then proceed with this artist
            if artist:
                if len(artist.songs) == 20:
                    break

            return {
                'artist': artist_name,
                'score': 0,
                'languages': ''
            }

        except Exception as e:
            print(e)

    # If artist found
    if artist:

        # Empty set for lemmas
        lemmas = set()

        # FOR DEBUGGING
        # with open(f"./{artist_name.replace('/', ' ')}_data.txt", 'w', encoding='utf-8') as file:
        #     file.write('')

        # Create empty list for languages
        languages = []

        # Write all song lyrics to temp string
        for song in artist.songs:
            try:
                temp = song.lyrics.split('\n', 1)[1]
            except Exception as e:
                print(e)
                temp = song.lyrics

            # Regular expression to remove text within square brackets (tags like 'Chorus', 'Verse' etc.)
            temp = re.sub(r'\[.*?\]', '', temp)

            # Create empty list for words
            doc = []

            # Detect language
            languages.append(detect(temp))

            # Launch tokenization depending on language
            if languages[-1] in ['en', 'fr', 'de', 'it', 'es', 'ru', 'ua']:
                match languages[-1]:
                    case 'en':

                        # Load the model for English language and tokenize text
                        try:
                            doc = nlp_en(temp)
                        except Exception as e:
                            print(e)
                            spacy.cli.download("en_core_web_sm")
                            nlp_en = spacy.load("en_core_web_sm")
                            doc = nlp_en(temp)

                    case 'fr':

                        # Load the model for French language and tokenize text
                        try:
                            doc = nlp_fr(temp)
                        except Exception as e:
                            print(e)
                            spacy.cli.download("fr_core_news_sm")
                            nlp_fr = spacy.load("fr_core_news_sm")
                            doc = nlp_fr(temp)

                    case 'de':

                        # Load the model for German language and tokenize text
                        try:
                            doc = nlp_de(temp)
                        except Exception as e:
                            print(e)
                            spacy.cli.download("de_core_news_sm")
                            nlp_de = spacy.load("de_core_news_sm")
                            doc = nlp_de(temp)

                    case 'es':

                        # Load the model for Spanish language and tokenize text
                        try:
                            doc = nlp_es(temp)
                        except Exception as e:
                            print(e)
                            spacy.cli.download("es_core_news_sm")
                            nlp_es = spacy.load("es_core_news_sm")
                            doc = nlp_es(temp)

                    case 'it':

                        # Load the model for Italian language and tokenize text
                        try:
                            doc = nlp_it(temp)
                        except Exception as e:
                            print(e)
                            spacy.cli.download("it_core_news_sm")
                            nlp_it = spacy.load("it_core_news_sm")
                            doc = nlp_it(temp)

                    case 'ru' | 'ua':

                        # Load the model for Russian language and tokenize text
                        try:
                            doc = nlp_ru(temp)
                        except Exception as e:
                            print(e)
                            spacy.cli.download("ru_core_news_sm")
                            nlp_ru = spacy.load("ru_core_news_sm")
                            doc = nlp_ru(temp)

                # Calculate the unique lemmas
                lemmas.update([token.lemma_ for token in doc if token.is_alpha and token.pos_ != 'X'])

                # FOR DEBUGGING
                # with open(f"./{artist_name.replace('/', ' ')}_data.txt", 'a', encoding='utf-8') as file:
                #     file.write(f'{song.title}, {languages[-1]}, {len(lemmas)}\n')

            else:
                del languages[-1]

            # Delete doc from memory
            del doc

            print(f'processing {song.title} - {len(lemmas)}')

        # Get rid of unnecessary data in memory
        try:
            del max_songs
        except Exception as e:
            print(e)

        try:
            del genius
        except Exception as e:
            print(e)

        try:
            del artist
        except Exception as e:
            print(e)

        try:
            del song
        except Exception as e:
            print(e)

        try:
            del temp
        except Exception as e:
            print(e)

        try:
            del nlp_en
        except Exception as e:
            print(e)

        try:
            del nlp_fr
        except Exception as e:
            print(e)

        try:
            del nlp_de
        except Exception as e:
            print(e)

        try:
            del nlp_it
        except Exception as e:
            print(e)

        try:
            del nlp_es
        except Exception as e:
            print(e)

        try:
            del nlp_ru
        except Exception as e:
            print(e)

        # Clear memory or something
        gc.collect()

        # Return the count of unique lemmas
        return {
            'artist': artist_name,
            'score': len(lemmas),
            'languages': set(languages)
        }

    # Otherwise it's sad
    else:
        return "Artist not found"

