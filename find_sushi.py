import argparse

from scorer import score_business
from yelp_api import YelpAPI

DEFAULT_LOCATION = 'Manhattan, NY'
NAME_LEN = 30

parser = argparse.ArgumentParser(description='Good sushi finder')
parser.add_argument(
    '-c',
    dest='city',
    default=DEFAULT_LOCATION,
    help='Specify a city to find sushi in (default: %s)' % DEFAULT_LOCATION,
    )
parser.add_argument(
    '-n',
    dest='neighborhood',
    help='Specify a Manhattan neighborhood to find sushi in (such as "Upper East Side")'
    )
parser.add_argument(
    '-#',
    dest='count',
    default=10,
    help='Number of restaurants to consider',
    )
parser.add_argument(
    '--rafi',
    dest='text_output',
    default=False,
    help='Give this a value if you\'re outputting for text',
    )

args = parser.parse_args()

def fix_length(s, n):
    chrs = [' ' if i >= len(s) else s[i] for i in range(n)]
    return ''.join(chrs)

location = args.city
if args.neighborhood != None:
    location = '%s, %s' % (args.neighborhood, DEFAULT_LOCATION)
limit = int(args.count)

api = YelpAPI()
options = []
while len(options) < limit:
    options += api.get_sushi_restaurants(location, len(options))

options = map(lambda biz: (score_business(biz), biz), options)
options = sorted(options, reverse=True)
for (score, biz) in options:
    chrs = [' ' if i >= len(biz.name) else biz.name[i] for i in range(NAME_LEN)]
    url = biz.url if args.text_output == False else '\n    %s' % biz.url
    print '%s%.3f: %s    %s  %s' % (
        ' ' if score >= 0 else '',
        score,
        fix_length(biz.name, NAME_LEN),
        fix_length(biz.get_dollars(), 5),
        url
        )
