
def score_business(business):
    count = 0
    for review in business.reviews:
        is_fresh = 'fresh' in review[1].lower()
        is_good_rating = review[0] >= 3.9

        if is_good_rating and is_fresh:
            count += 1
        if not is_good_rating and is_fresh:
            count -= 1
    return count * 1.0 / len(business.reviews)
