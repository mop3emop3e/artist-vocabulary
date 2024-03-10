from lyricsgenius import Genius
import spacy
import re
import os

# Access token for genius.com
CLIENT_ACCESS_TOKEN = os.environ.get('CLIENT_ACCESS_TOKEN')


def get_artist_score(artist_name, language='en', max_songs=None):
    """
    Get number of unique words used by artists in all songs
    :return: number of all unique words
    """

    # Create Genius object
    genius = Genius(CLIENT_ACCESS_TOKEN)

    # Set number of retries
    genius.retries = 20

    # Get artist object by name
    while True:

        # Try until good response
        try:
            artist = genius.search_artist(artist_name, max_songs=max_songs)
            break
        except Exception as e:
            print(e)

    # If artist found
    if artist:

        # Empty string for all lyrics
        temp = ''

        # Write all song lyrics to temp string
        for song in artist.songs:

            # Try to get rid of the 1st line since it's always some information and not the actual lyrics
            try:
                temp += song.lyrics.split('\n', 1)[1]
            except:
                temp += song.lyrics

        # FOR DEBUGGING
        # with open(f"./{artist_name.replace('/', ' ')}_temp_lyrics.txt", 'w', encoding='utf-8') as file:
        #     file.write(temp)

        # Regular expression to remove text within square brackets (tags like 'Chorus', 'Verse' etc.)
        temp = re.sub(r'\[.*?\]', '', temp)

        # Create empty list for words
        doc = []

        # Launch tokenization depending on language
        match language:
            case 'en':

                # Regular expression to remove Cyrillic characters but keep Latin characters, including those with diacritics
                temp = re.sub(r'[А-Яа-яЁё]+', '', temp)

                # Load the model for English language
                try:
                    nlp_en = spacy.load("en_core_web_sm")
                except Exception as e:
                    print(e)
                    spacy.cli.download("en_core_web_sm")
                    nlp_en = spacy.load("en_core_web_sm")

                # Increase maximum length of string for analysis
                nlp_en.max_length = 5000000
                doc = nlp_en(temp)
            case 'fr':

                # Regular expression to remove Cyrillic characters but keep Latin characters, including those with diacritics
                temp = re.sub(r'[А-Яа-яЁё]+', '', temp)

                # Load the model for French language
                try:
                    nlp_fr = spacy.load("fr_core_news_sm")
                except Exception as e:
                    print(e)
                    spacy.cli.download("fr_core_news_sm")
                    nlp_fr = spacy.load("fr_core_news_sm")

                # Increase maximum length of string for analysis
                nlp_fr.max_length = 5000000
                doc = nlp_fr(temp)
            case 'de':

                # Regular expression to remove Cyrillic characters but keep Latin characters, including those with diacritics
                temp = re.sub(r'[А-Яа-яЁё]+', '', temp)

                # Load the model for German language
                try:
                    nlp_de = spacy.load("de_core_news_sm")
                except Exception as e:
                    print(e)
                    spacy.cli.download("de_core_news_sm")
                    nlp_de = spacy.load("de_core_news_sm")

                # Increase maximum length of string for analysis
                nlp_de.max_length = 5000000
                doc = nlp_de(temp)
            case 'es':

                # Regular expression to remove Cyrillic characters but keep Latin characters, including those with diacritics
                temp = re.sub(r'[А-Яа-яЁё]+', '', temp)

                # Load the model for Spanish language
                try:
                    nlp_es = spacy.load("es_core_news_sm")
                except Exception as e:
                    print(e)
                    spacy.cli.download("es_core_news_sm")
                    nlp_es = spacy.load("es_core_news_sm")

                # Increase maximum length of string for analysis
                nlp_es.max_length = 5000000
                doc = nlp_es(temp)
            case 'it':

                # Regular expression to remove Cyrillic characters but keep Latin characters, including those with diacritics
                temp = re.sub(r'[А-Яа-яЁё]+', '', temp)

                # Load the model for Italian language
                try:
                    nlp_it = spacy.load("it_core_news_sm")
                except Exception as e:
                    print(e)
                    spacy.cli.download("it_core_news_sm")
                    nlp_it = spacy.load("it_core_news_sm")

                # Increase maximum length of string for analysis
                nlp_it.max_length = 5000000
                doc = nlp_it(temp)
            case 'ru':

                # Regular expression to match non-Cyrillic characters and replace them with nothing
                temp = re.sub(r'[^\u0400-\u04FF\s.,!?;:\-\'"()\\[\]]+', '', temp)

                # Load the model for Russian language
                try:
                    nlp_ru = spacy.load("ru_core_news_sm")
                except Exception as e:
                    print(e)
                    spacy.cli.download("ru_core_news_sm")
                    nlp_ru = spacy.load("ru_core_news_sm")

                # Increase maximum length of string for analysis
                nlp_ru.max_length = 5000000
                doc = nlp_ru(temp)

        # Calculate the unique lemmas
        lemmas = [token.lemma_ for token in doc if token.is_alpha]
        unique_lemmas = set(lemmas)

        # FOR DEBUGGING
        # with open('./temp_lemmas.txt', 'w', encoding='utf-8') as file:
        #     for lemma in unique_lemmas:
        #         file.write(f'{lemma}\n')

        # Print the count of unique lemmas
        return len(unique_lemmas)

    # Otherwise it's sad
    else:
        return "Artist not found"
