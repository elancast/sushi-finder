import json
import oauth2
import urllib2

from browser import get_browser, open_page
import html_helper
from yelp_business import YelpBusiness

# 4 lines consisting of yelp: consumer key, consumer secret, token, token secret
BUSINESS_URL = 'http://api.yelp.com/v2/business/%s'
FILE = '.yelpkeys.secret'
RATING_SORT = 2
SEARCH_URL = 'http://api.yelp.com/v2/search'
YELP_URL = 'http://www.yelp.com/biz/%s'

class YelpAPI:
    def __init__(self):
        self._br = get_browser()
        self._init_yelp_keys_stuff()

    def _init_yelp_keys_stuff(self):
        f = open(FILE, 'r')
        lines = f.read().strip().split('\n')
        self._consumer_key = lines[0]
        self._consumer_secret = lines[1]
        self._token = lines[2]
        self._token_secret = lines[3]

    def get_sushi_restaurants(self):
        data = self._open_api_url(self._get_search_url())
        list = []
        for item in data['businesses']:
            business = YelpBusiness(item)
            business.set_reviews(self._get_reviews(business.id))
            list.append(business)
        return list

    def get_restaurant_details(self, id):
        url = self._get_authorized_url(BUSINESS_URL % id)
        data = self._open_api_url(url)
        business = YelpBusiness(data)
        business.set_reviews(self._get_reviews(business.id))
        return business

    def _get_search_url(self):
        data = {
            'term': 'sushi',
            'location': 'Manhattan, NY',
            'sort': RATING_SORT,
            }
        return self._get_authorized_url(SEARCH_URL, data)
        
    def _get_authorized_url(self, url, data = {}):
        oauth_request = oauth2.Request('GET', url, {})
        data['oauth_nonce'] = oauth2.generate_nonce()
        data['oauth_timestamp'] = oauth2.generate_timestamp()
        data['oauth_token'] = self._token
        data['oauth_consumer_key'] = self._consumer_key
        oauth_request.update(data)

        consumer = oauth2.Consumer(self._consumer_key, self._consumer_secret)
        token = oauth2.Token(self._token, self._token_secret)
        oauth_request.sign_request(oauth2.SignatureMethod_HMAC_SHA1(),
                                   consumer,
                                   token)
        return oauth_request.to_url()

    def _open_api_url(self, url):
        resp = urllib2.urlopen(url)
        s = resp.read()
        resp.close()
        return json.loads(s)

    def _get_reviews(self, id):
        s = open_page(self._br, YELP_URL % id)
        reviews = []

        s = s[s.index('<h2>Recommended Reviews'):]
        while True:
            (stars, s) = html_helper.advance_and_find(s, 'itemprop="ratingValue"', 'content="', '"')
            if stars == None:
                break
            stars = float(stars)
            
            (descr, s) = html_helper.advance_and_find(s, 'itemprop="description"', '>', '</p')
            reviews.append((stars, descr))
        return reviews

if __name__ == '__main__':
    YelpAPI().get_sushi_restaurants()