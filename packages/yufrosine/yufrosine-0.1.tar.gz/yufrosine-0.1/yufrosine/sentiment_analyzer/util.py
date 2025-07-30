def score_to_good_bad_rating(score):
    if score > 0.5:
        return "Very Good"
    if score > 0.1:
            return "Good"
    if score > -0.1:
                return "Neutral"
    if score > -0.5:
                return "Bad"
    return "very Bad"