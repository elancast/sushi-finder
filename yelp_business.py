
class YelpBusiness:
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.url = data['url']
        self.rating = data['rating']
        self.reviews_count = data['review_count']
        self.categories = map(lambda i: i[-1], data['categories'])

        self.address_lines = data['location']['display_address']
        self.latitude = data['location']['coordinate']['latitude']
        self.longitude = data['location']['coordinate']['longitude']

        self.reviews = []
        self.menu = []

    def set_reviews(self, reviews):
        self.reviews = reviews

    def set_menu(self, menu):
        self.menu = menu
