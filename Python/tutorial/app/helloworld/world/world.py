import csv
from pathlib import Path

def translate_hello():
    """Reads the translation CSV database, transforms it into a dict and
    returns it.

    :returns: 'hello' translation dict
    """
    result = {}

    filename = Path(__file__).parent / '../../data/translate.csv'
    with open(filename) as csvfile:
        reader = csv.reader(csvfile)

        for row in reader:
            result[row[0]] = row[1]

    return result
