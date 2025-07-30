from .base import SentimentAnalyzer
from .util import score_to_good_bad_rating
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from collections import defaultdict
import statistics

class VaderAnalyzer(SentimentAnalyzer):
    def get_score_string(self, text: str) -> float:
        analyzer = SentimentIntensityAnalyzer()
        return analyzer.polarity_scores(text)['compound']

    def get_label_string(self, text: str) -> str:
        return score_to_good_bad_rating(self.get_score(text))
    

    def get_score_list_dict(self, content: list[dict]) -> list[dict]:
        sentiment_scores = defaultdict(list)

        for article in content:
            title = article.get("title", "")
            description = article.get("description", "")
            combined_text = f"{title}. {description}"

            score = self.get_score_string(combined_text)

            for company in article["companies"]:
                sentiment_scores[company].append(score)

        return {
            company: statistics.mean(scores)
            for company, scores in sentiment_scores.items()
        }


    def get_label_list_dict(self, content: list[dict]) -> list[dict]:
        sentiment_scores = defaultdict(list)
        analyzer = SentimentIntensityAnalyzer()

        sentiment_scores_return = defaultdict(float)

        for article in content:
            title = article.get("title", "")
            description = article.get("desciption", "")

            combined_text = f"{title}. {description}"
            
            score = self.get_score_string(combined_text)

            for company in article["companies"]:
                sentiment_scores[company].append(score)
        
        for company in sentiment_scores:
            sentiment_scores_return[company] = score_to_good_bad_rating(statistics.mean(sentiment_scores[company]))

        return dict(sentiment_scores_return)