from scorer import score_business
from yelp_api import YelpAPI

nice_restaurants = [
    'sushi-yasuda-new-york',
    'sakagura-new-york',
    'tenroku-sushi-san-francisco',
    'daigo-sushi-san-francisco',
    'sushi-masu-los-angeles',
    'sushi-nakazawa-new-york',
    'yuba-new-york-2',
    'o-toro-sushi-san-francisco',
    'sushi-of-gari-tribeca-new-york-2',
    'saru-sushi-bar-san-francisco',
    ]

api = YelpAPI()

businesses = []
for biz in nice_restaurants:
    business = api.get_restaurant_details(biz)
    businesses.append((score_business(business), business))

businesses = sorted(businesses, reverse=True)
for (score, biz) in businesses:
    print '%s%.3f: %s' % (' ' if score >= 0 else '', score, biz.name)
