
class YelpBusiness:
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.url = data['url']
        self.rating = data['rating']
        self.reviews_count = data['review_count']

        self.address_lines = data['location']['display_address']
        self.latitude = data['location']['coordinate']['latitude']
        self.longitude = data['location']['coordinate']['longitude']

    def set_reviews(self, reviews):
        self.reviews = reviews
