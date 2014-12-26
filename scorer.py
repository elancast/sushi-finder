
class ScoreFactor:
    def get_score_contribution(self, business):
        score = self._get_numerator(business) * 1.0 / self._get_denominator(business)
        return score * self.weight

    def get_score_weight(self, business):
        return max(0, self.weight)

    def _get_denominator(self, business):
        return 1

    def _get_numerator(self):
        raise RuntimeError('This should be implemented')

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

    def _get_numerator(self, business):
        total = 0
        for review in business.reviews:
            if self._matches_review(review[0], review[1]):
                total += 1
        return total

    def _get_denominator(self, business):
        return len(business.reviews)

    def _matches_review(self, rating, text):
        match = self.phrase in text.lower()
        is_good_rating = rating >= 3.9
        if self.needs_good_rating:
            return match and is_good_rating
        if self.needs_bad_rating:
            return match and not is_good_rating
        return match

class MenuScoreFactor(ScoreFactor):
    def __init__(self, words, weight):
        self.words = words
        self.weight = weight

    def _get_numerator(self, business):
        total = 0
        for item in business.menu:
            for word in self.words:
                if word in item.lower():
                    total += 1
                    break
        return total * .05

class NoMenuPenalty(ScoreFactor):
    def __init__(self, weight):
        self.weight = weight

    def _get_numerator(self, business):
        return 0 if len(business.menu) > 0 else -1

class CategoryPenalty(ScoreFactor):
    def __init__(self, weight):
        self.weight = weight

    def _get_numerator(self, business):
        if 'thai' in business.categories:
            return 1
        return 0

class BadRatingPenalty(ScoreFactor):
    def __init__(self, weight):
        self.weight = weight

    def _get_numerator(self, business):
        if business.reviews_count < 25: return 1
        if business.reviews_count < 50: return .5
        if business.rating < 3.9:       return .5
        return 0

BAD_MENU_WORDS = ['teriyaki', ' don', 'chicken', 'soba', 'udon', 'fried']
GOOD_MENU_WORDS = [
    'king salmon',
    'hotate', 'scallop',
    'saba', 'mackerel',
    'umimasu', 'trout',
    'uni', 'sea urchin',
    ]

FACTORS = [
    ReviewScoreFactor(' fresh', 1, needs_good_rating=True),
    ReviewScoreFactor(' fresh', -1, needs_bad_rating=True),
    ReviewScoreFactor('tradition', .5, needs_good_rating=True),
    MenuScoreFactor(BAD_MENU_WORDS, -.5),
    NoMenuPenalty(.25),
    CategoryPenalty(-.5),
    MenuScoreFactor(GOOD_MENU_WORDS, .5),
    BadRatingPenalty(-.5)
    ]

def score_business(business):
    (total, weights) = (0, 0)
    for (i, factor) in enumerate(FACTORS):
        total += factor.get_score_contribution(business)
        weights += factor.get_score_weight(business)
    # return total * 1.0 / weights
    return total
