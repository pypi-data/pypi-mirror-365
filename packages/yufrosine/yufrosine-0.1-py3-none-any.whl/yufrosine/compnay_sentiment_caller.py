#   Simple Sentiment caller
#
#   Author: Daniel Popa
#
#   May 16, 2025
#
#  This prigram takes between 100 and 500 articles, and searches for the most mentioned. It then compiles
#  a list of the sentiment for each company in the news 
#

from newsapi import NewsApiClient
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import os
from datetime import datetime, timedelta
import spacy
import pandas as pd
from collections import defaultdict
import statistics

nlp = spacy.load("en_core_web_sm")

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
    
def load_company_list(filename = "smp500.csv"):
    df = pd.read_csv(filename)
    return set(df["Security"].dropna().str.strip())

def get_articles(request_size = 30):
    #note max request size is 100 for newsapi, must split others into parts
    triggers = "stock OR market OR finance OR earnings OR economy"

    newsapi = NewsApiClient(api_key = get_key(NEWSAPI_KEY_FILE))

    response = newsapi.get_everything(q=triggers, language='en', page_size=request_size)
    return response["articles"]

def extract_companies_from_string(text):
    doc = nlp(text)
    companies = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
    return companies

def extract_cmpanies_from_listofdict(articles):
    company_mentions = []

    for article in articles:
        title = article.get("title", "")
        description = article.get("description", "")
        combined_text = f"{title} {description}"

        companies = extract_companies_from_string(combined_text)

        if len(companies) > 0:
            company_mentions.append({
                "title": title,
                "description": description,
                "companies": companies
            })
    
    return company_mentions

def filter_compy_mentions(article_list, whitelist):
    cleaned_companies = []

    for article in article_list:
        matched_companies = [];
        for found in article["companies"]:
            for security in whitelist:
                if security.lower() in found.lower():
                    matched_companies.append(security)

                    #stop searching after first match
                    break 
    
        if matched_companies:
            article["companies"] = list(set(matched_companies))
            cleaned_companies.append(article)
    
    return cleaned_companies

#Alaizes text using vader, better for titles
def analyze_sentiment_vader(pairs):
    results = []
    analyzer = SentimentIntensityAnalyzer()
    for title, description in pairs:
        combined_text = title#f"{title}. {description}"
        score = analyzer.polarity_scores(combined_text)['compound']
        results.append((title, score))
    return results

def calc_each_company_frequency(cleaned_companies):
    counts = defaultdict(int)

    for article in cleaned_companies:
        for company in article["companies"]:
            counts[company] += 1
    
    return dict(counts)

def calc_each_company_score(cleaned_companies):
    sentiment_scores = defaultdict(list)
    analyzer = SentimentIntensityAnalyzer()

    sentiment_scores_return = defaultdict(float)

    for article in cleaned_companies:
        title = article.get("title", "")
        description = article.get("desciption", "")

        combined_text = f"{title}. {description}"
        
        score = analyzer.polarity_scores(combined_text)['compound']

        for company in article["companies"]:
            sentiment_scores[company].append(score)
    
    for company in sentiment_scores:
        sentiment_scores_return[company] = statistics.mean(sentiment_scores[company])

    return dict(sentiment_scores_return)

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

def calc_each_company_good_bad_rating(cleaned_companies):
    sentiment_scores = defaultdict(list)
    analyzer = SentimentIntensityAnalyzer()

    sentiment_scores_return = defaultdict(float)

    for article in cleaned_companies:
        title = article.get("title", "")
        description = article.get("desciption", "")

        combined_text = f"{title}. {description}"
        
        score = analyzer.polarity_scores(combined_text)['compound']

        for company in article["companies"]:
            sentiment_scores[company].append(score)
    
    for company in sentiment_scores:
        sentiment_scores_return[company] = score_to_good_bad_rating(statistics.mean(sentiment_scores[company]))

    return dict(sentiment_scores_return)

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
    #print(load_company_list())
    articles = extract_cmpanies_from_listofdict(get_articles(request_size=100))
    print (articles)
    print("-----------------")
    cleaned_companies = filter_compy_mentions(articles, load_company_list())
    print(cleaned_companies)
    print("-----------------")

    frequency = calc_each_company_frequency(cleaned_companies)
    print(frequency)

    print("-----------------")
    scores_list = calc_each_company_score(cleaned_companies)
    print(scores_list)

    print("-----------------")
    scores_list = calc_each_company_good_bad_rating(cleaned_companies)
    print(scores_list)


if __name__ == "__main__":
    run()
