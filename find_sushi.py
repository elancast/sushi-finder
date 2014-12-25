import argparse

from scorer import score_business
from yelp_api import YelpAPI

DEFAULT_LOCATION = 'Manhattan, NY'
NAME_LEN = 20

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

args = parser.parse_args()

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
    print '%s%.3f: %s     %s' % (' ' if score >= 0 else '', score, ''.join(chrs), biz.url)
