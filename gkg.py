""" Example of Python client calling Knowledge Graph Search API """

import sys, json, argparse
import argparse

from urllib.request import urlopen
from urllib.parse import urlencode

SERVICE_URL = 'https://kgsearch.googleapis.com/v1/entities:search'


USAGE = """USAGE: python gkg.py 'Springfield IL' --n 10 --types 'Organization Place' --languages = 'ru' """

# read api key from file
default_api_key = open('.api_key').read().rstrip()

default_types = []  # defaults to 'Thing'
default_languages = []  # service defaults to en
default_limit = 2

# Current types include all of the schema.org types. These are some of them.
# See all the schema.org types here: https://schema.org/docs/full.html

typestrings = """Action|AdministrativeArea|Animal|BodyOfWater|Book|Brand|CollegeOrUniversity|Corporation|Corporation|Country|CreativeWork|EducationalOrganization|Event|Intangible|MedicalEntity|Movie|MovieTheater|MusicAlbum|MusicComposition|Organization|PerformingGroup|Periodical|Person|Place|Product|ProductModelRiverBodyOfWater|Religion|SoftwareApplication|SportsOrganization|SportsTeam|Thing|TVSeries|Vehicle|VideoGame"""

gkg_types = set('|'.split(typestrings))

def gkg_query(query, limit, types, languages, key):
    """ returns a JSON object with data from the google knowledge graph """
    params = {'query':query, 'limit':limit, 'key':key, 'types':types}
    query_url = SERVICE_URL + '?' +  urlencode(params)
    # we have to add the languages manually, since there may be more than one
    if languages and type(languages) == str:
        languages = languages.split(' ')
    if languages:
        for lang in languages:
            query_url += f"&languages={lang}"
    print('QUERY_URL:', query_url)
    return json.loads(urlopen(query_url).read())["itemListElement"]


def gkg(query, limit=default_limit, types=default_types, languages='', key=default_api_key):
    # simplifies the response by returning just a list of hits,
    # removing some properties and using @language for the detailed
    # description language property """
    results = []
    for element in gkg_query(query, limit, types, languages, default_api_key):
        result = element['result']
        result['resultscore'] = element['resultScore']
        if 'detailedDescription' in result:
            simplify_detailed_description(result['detailedDescription'])
        results.append(result)
    return results

def simplify_detailed_description(dd):
    "result of ocd"
    if type(dd) == list:
        for item in dd: simplify_detailed_description(item)
    else:
        del dd['license']
        if 'inLanguage' in dd:
            dd['@language'] = dd['inLanguage']
            del dd['inLanguage']

def main(query, n, types, languages):
    hits = gkg(query, n, types, languages)
    print(json.dumps(hits, indent = 2, separators=(",", ":"), sort_keys=True, ensure_ascii=False))


if __name__ == '__main__':
    a = argparse.ArgumentParser(description='query google knowledge graph')
    a.add_argument('query', help='string for search')
    a.add_argument('-n', '--n', nargs='?', default=default_limit, help="how many results")
    a.add_argument('-t', '--types',  nargs='?', default="Thing", help="possible types separated by spaces (e/g, 'Person Place')")
    a.add_argument('-l', '--languages',  nargs='?', default="en", help="languages for strings separated by spaces (e.g., 'en ru zh')")    
    args = a.parse_args()
    main(args.query, args.n, args.types, args.languages)

