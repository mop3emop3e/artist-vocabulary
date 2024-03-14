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
            break
        except Exception as e:
            print(e)

    # If artist found
    if artist:

        # Empty set for lemmas
        lemmas = set()

        # FOR DEBUGGING
        # with open(f"./{artist_name.replace('/', ' ')}_temp_lyrics.txt", 'w', encoding='utf-8') as file:
        #     file.write('')

        # Write all song lyrics to temp string
        for song in artist.songs:

            # Try to get rid of the 1st line since it's always some information and not the actual lyrics
            try:
                temp = song.lyrics.split('\n', 1)[1]
            except:
                temp = song.lyrics

            # FOR DEBUGGING
            # with open(f"./{artist_name.replace('/', ' ')}_temp_lyrics.txt", 'a', encoding='utf-8') as file:
            #     file.write(f'{temp}\n')

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
                    doc = nlp_ru(temp)

            # Calculate the unique lemmas
            lemmas.update([token.lemma_ for token in doc if token.is_alpha and token.pos_ != 'X'])

        # FOR DEBUGGING
        # with open('./temp_lemmas.txt', 'w', encoding='utf-8') as file:
        #     for lemma in lemmas:
        #         file.write(f'{lemma}\n')

        # Return the count of unique lemmas
        return len(lemmas)

    # Otherwise it's sad
    else:
        return "Artist not found"
