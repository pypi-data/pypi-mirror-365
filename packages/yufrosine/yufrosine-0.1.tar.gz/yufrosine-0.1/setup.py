from setuptools import setup, find_packages

setup(
    name="yufrosine",
    version="0.1",
    author = "Daniel Popa",
    description= "lightweight sentiment analysis tool for financial news",
    long_description= open("README.txt").read(),
    long_description_content_type="text/markdown",
    url = "https://github.com/websmartprint/Sentiment-Analyzer",
    packages=find_packages(),
    install_requires=[
        "spacy",
        "pandas",
        #"textblob",
        "vaderSentiment",
        "newsapi-python"
    ],
    python_requires=">=3.8"
)
