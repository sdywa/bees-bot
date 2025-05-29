import re


def clean_text(text):
    return re.sub('[^0-9а-яА-Я ()]', '', text).lower().strip()