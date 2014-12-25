
class ScoreFactor:
    def matches_review(self, rating, text):
        return False

    def get_menu_items_score(self, menu_items):
        return False

    def get_weight(self):
        return self.weight if self.weight >= 0 else 0

class ReviewScoreFactor(ScoreFactor):
    def __init__(self,
                 phrase,
                 weight,
                 needs_good_rating=False,
                 needs_bad_rating=False,
                 ):
        self.phrase = phrase
        self.needs_good_rating = needs_good_rating
        self.needs_bad_rating = needs_bad_rating
        self.weight = weight

    def matches_review(self, rating, text):
        match = self.phrase in text.lower()
        is_good_rating = rating >= 3.9
        if self.needs_good_rating:
            return match and is_good_rating
        if self.needs_bad_rating:
            return match and not is_good_rating
        return match

    def get_contribution(self, score, reviews_len):
        matching_fraction = score * 1.0 / reviews_len
        return matching_fraction * self.weight

class MenuScoreFactor(ScoreFactor):
    def __init__(self, fn, weight):
        self.weight = weight
        self.fn = fn

    def get_menu_items_score(self, menu_items):
        return self.fn(menu_items)

    def get_contribution(self, score, reviews_len):
        return score * self.weight

BAD_MENU_WORDS = ['teriyaki', ' don']
def _score_by_elimination(menu_items):
    count = 0
    for item in menu_items:
        menu_item = item.lower()
        for word in BAD_MENU_WORDS:
            if menu_item.find(word) >= 0:
                count += 1
                break
    return 0 if len(menu_items) == 0 else count * 1.0 / len(menu_items)

FACTORS = [
    ReviewScoreFactor(' fresh', 1, needs_good_rating=True),
    ReviewScoreFactor(' fresh', -1, needs_bad_rating=True),
    ReviewScoreFactor('tradition', .5, needs_good_rating=True),
    MenuScoreFactor(_score_by_elimination, -1),
    ]

def score_business(business):
    scores = [0 for i in range(len(FACTORS))]
    for i in range(len(FACTORS)):
        factor = FACTORS[i]
        for review in business.reviews:
            if factor.matches_review(review[0], review[1]):
                scores[i] += 1
        scores[i] += factor.get_menu_items_score(business.menu)

    (total, weights) = (0, 0)
    for i in range(len(FACTORS)):
        factor = FACTORS[i]
        total += factor.get_contribution(scores[i], len(business.reviews))
        weights += factor.get_weight()
    return total / weights
