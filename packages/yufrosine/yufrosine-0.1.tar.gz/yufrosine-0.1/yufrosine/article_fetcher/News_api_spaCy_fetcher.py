from newsapi import NewsApiClient
import os
from datetime import datetime, timedelta
import spacy
import pandas as pd
from collections import defaultdict
import statistics

from .base import ArticleFetcher

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

def load_company_list(filename="s&p500.csv"):
    filepath = os.path.join(os.path.dirname(__file__), filename)
    df = pd.read_csv(filepath)
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

class NewsApiSpaCyFetcher(ArticleFetcher):

    def company_and_article_list(self, sample_size: int = 50) -> list[dict]:
        articles = extract_cmpanies_from_listofdict(get_articles(request_size= sample_size))
        cleaned_companies = filter_compy_mentions(articles, load_company_list())

        return cleaned_companies

def run():
    #print(load_company_list())
    articles = extract_cmpanies_from_listofdict(get_articles(request_size=100))
    print (articles)
    print("-----------------")
    cleaned_companies = filter_compy_mentions(articles, load_company_list())
    print(cleaned_companies)
    print("-----------------")


if __name__ == "__main__":
    run()

