from scorer import score_business
from yelp_api import YelpAPI

nice_restaurants = [
    'tenroku-sushi-san-francisco',
    'daigo-sushi-san-francisco',
    'sushi-masu-los-angeles',
    'sushi-nakazawa-new-york',
    'yuba-new-york-2',
    'o-toro-sushi-san-francisco',
    'sushi-of-gari-tribeca-new-york-2',
    ]

api = YelpAPI()
for biz in nice_restaurants:
    business = api.get_restaurant_details(biz)
    print '%s: %.3f' % (business.name, score_business(business))
