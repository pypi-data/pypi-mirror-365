#   Simple Sentiment Analizer
#
#   Author: Daniel Popa
#
#   May 6, 2025
#
#  Has methods using two libraies (vader and textblob) that use word analysis to see how positive or negative sentiment is on a compeny
#  It pulls ten most recent headlines in articles conatiing a mention of the company, and rates the avarge sentiment of those headlines from 
#  1 (very good) to -1 (very bad). It worth noting that this is WORD ANALYSIS, things like the actual meaning of the healdine, and sacrasm, jokes, etc
#  are not recognized by this program. It finds the average sentiment of the individual words themselves. 
#

from newsapi import NewsApiClient
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
NEWSAPI_KEY_FILE = os.path.join(SCRIPT_DIR, "News_API_Key.txt")

def get_key(filename):

    if not os.path.exists(filename):
    #Create file
        with open (filename, "w") as f:
            f.write(f"YOUR API kere for {filename}")
        raise FileNotFoundError(f"{filename} not found, {filename} created, please insert api key")
    
    with open(filename, "r") as api_key_file:
        key = api_key_file.read()
        if not key:
            raise ValueError(f"{filename} exists but no api  key found")
        return key

def get_articles(company_name):

    newsapi = NewsApiClient(api_key = get_key(NEWSAPI_KEY_FILE))

    response = newsapi.get_everything(q=company_name, language='en', page_size=10)

    return [
        (a['title'], a['description'] or "")  # Avoid NoneType errors
        for a in response['articles']
    ]  

#Kept just in case, not used becuase less accurate, analizes sentiment using blob
def analyze_sentiment_blob(pairs):
    results = []
    for title, description in pairs:
        combined_text = f"{title}. {description}"
        score = TextBlob(combined_text).sentiment.polarity  # Range: -1 to +1
        results.append((title, score))
    return results

#Alaizes text using vader, better for titles
def analyze_sentiment_vader(pairs):
    results = []
    analyzer = SentimentIntensityAnalyzer()
    for title, description in pairs:
        combined_text = title#f"{title}. {description}"
        score = analyzer.polarity_scores(combined_text)['compound']
        results.append((title, score))
    return results

#prints a summary of the results of the sentiment search
def print_summary(results):
    total = 0
    print("\nSentiment Scores:\n")
    for title, score in results:
        print(f"[{score:+.2f}] {title}")
        total += score
    avg = total / len(results) if results else 0
    print(f"\nAverage Sentiment Score: {avg:+.2f}")
    return avg

#calculates average score
def avg_score(results):
   for title, score in results:
        print(f"[{score:+.2f}] {title}")
        total += score
   avg = total / len(results) if results else 0
   return avg

#Turns the score into an actual string saying good, bad, neutral, etc.
# This is done so its easier to read, rather than seeing a number
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

#This method does the wole process, given a company name, does the search, and return the sentiment as an integer
def get_score(company_name):
     articles = get_articles
     results = analyze_sentiment_vader(articles)
     return avg_score(results)

# Same as get_score, but return a string saying good, bad, neutral, etc
def get_good_bad_rating(company_name):
     articles = get_articles
     results = analyze_sentiment_vader(articles)
     return score_to_good_bad_rating(avg_score(results))

#If run locally, this is the test
def run():
    company = input("Enter a company name: ")
    articles = get_articles(company)
    results = analyze_sentiment_vader(articles)
    vaderavg = print_summary(results)
    print(f"The average sentiment is - {score_to_good_bad_rating(vaderavg)}")
    print("--------------------")
    print()

if __name__ == "__main__":
    run()
