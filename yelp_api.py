import json
import oauth2
import urllib2

from browser import get_browser, open_page
from db_store import DBStore
import html_helper
from yelp_business import YelpBusiness

# 4 lines consisting of yelp: consumer key, consumer secret, token, token secret
BUSINESS_URL = 'http://api.yelp.com/v2/business/%s'
FILE = '.yelpkeys.secret'
MENU_URL = 'http://www.yelp.com/menu/%s'
RATING_SORT = 2
SEARCH_URL = 'http://api.yelp.com/v2/search'
YELP_BASE = 'http://www.yelp.com'
YELP_URL = 'http://www.yelp.com/biz/%s'

class YelpAPI:
    def __init__(self):
        self._br = get_browser()
        self._db = DBStore()
        self._init_yelp_keys_stuff()

    def _init_yelp_keys_stuff(self):
        f = open(FILE, 'r')
        lines = f.read().strip().split('\n')
        self._consumer_key = lines[0]
        self._consumer_secret = lines[1]
        self._token = lines[2]
        self._token_secret = lines[3]

    def get_sushi_restaurants(self, location, offset=0):
        print self._get_search_url(location, offset)
        data = self._open_api_url(self._get_search_url(location, offset))
        list = []
        for item in data['businesses']:
            business = YelpBusiness(item)

            (reviews, price) = self._get_more_details(business.id)
            business.set_reviews(reviews)
            business.set_price_level(price)
            business.set_menu(self._get_menu(business.id))
            list.append(business)
        return list

    def get_restaurant_details(self, id):
        url = self._get_authorized_url(BUSINESS_URL % id)
        data = self._open_api_url(url)
        business = YelpBusiness(data)

        (reviews, price) = self._get_more_details(business.id)
        business.set_reviews(reviews)
        business.set_price_level(price)
        business.set_menu(self._get_menu(business.id))
        return business

    def _get_search_url(self, location, offset):
        data = {
            'term': 'Sushi Bars',
            'location': location,
            # 'sort': RATING_SORT,
            'offset': offset,
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

    def _get_menu(self, id):
        cached_items = self._db.get_menu_items(id)
        if cached_items != None:
            return cached_items

        try:
            s = open_page(self._br, MENU_URL % id)
        except:
            s = ''

        items = set(self._get_menu_page(s))
        if 'class="sub-menus">' in s:
            while True:
                (link, s) = html_helper.advance_and_find(s, 'sub-menu', 'href="', '"')
                if link == None: break

                sub_menu = open_page(self._br, YELP_BASE + link)
                items = items.union(self._get_menu_page(sub_menu))

        if '' in items: items.remove('')
        self._db.save_menu_items(id, items)
        return map(lambda i: i, items)

    def _get_menu_page(self, s):
        items = []
        while True:
            (item, s) = html_helper.advance_and_find(s, 'class="media-story"', '<h3>', '</h3>')
            if item == None:
                break
            items.append(html_helper.strip_tags(item).strip())
        return items

    def _open_api_url(self, url):
        resp = urllib2.urlopen(url)
        s = resp.read()
        resp.close()
        s = s.decode('utf-8', 'replace').encode('ascii', 'replace')
        return json.loads(s)

    def _get_more_details(self, id):
        cached_reviews = self._db.get_reviews(id)
        cached_price_level = self._db.get_price_level(id)
        if len(cached_reviews) > 0 and cached_price_level != None:
            return (cached_reviews, cached_price_level)

        s = open_page(self._br, YELP_URL % id)
        (dollars, s) = html_helper.advance_and_find(s, 'itemprop="priceRange"', '>', '<')
        price_level = len(dollars)

        reviews = []
        s = s[s.index('<h2>Recommended Reviews'):]
        while True:
            (stars, s) = html_helper.advance_and_find(s, 'itemprop="ratingValue"', 'content="', '"')
            if stars == None:
                break
            stars = int(float(stars))

            (descr, s) = html_helper.advance_and_find(s, 'itemprop="description"', '>', '</p')
            reviews.append((stars, descr))

        self._db.save_reviews(id, reviews)
        self._db.save_price_level(id, price_level)
        return (reviews, price_level)

if __name__ == '__main__':
    YelpAPI().get_sushi_restaurants()
