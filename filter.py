import pandas as pd
import extruct
import requests
import re
from w3lib.html import get_base_url
from urllib.parse import urlparse

# Put valid urls into list here.
sites = []

# Extract metadata from url.
def extract_metadata(url):
    r = requests.get(url)
    base_url = get_base_url(r.text, r.url)
    metadata = extruct.extract(r.text,
                               base_url=base_url,
                               uniform=True,
                               syntaxes=['json-ld',
                                         'microdata',
                                         'opengraph'])
    return metadata, str(metadata)

def keyExists(dict, key):
    if not any(item['@type'] == key for item in dict):
        return False
    else:
        return True

# Determine if URL is a recipe or not based on content of metadata.
def isRecipe(s):
    query = re.search("\'@type\': \[.*'Recipe\'", s)
    if query == None:
        return False
    else:
        return True

# Iterate through sites and determine if they are recipes or not. Recipe pages will go to standard output appended with "True".
def exec():
    for url in sites:
        metadata, string = extract_metadata(url)
        bool = isRecipe(string)
        print(str(bool) + " " + url)

# Execute function.
if __name__ == "__main__":
    exec()
