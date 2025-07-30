# Yufrosine

Yufrosine is a lightweight sentiment analysis toolkit for financial news and stock filtering. It includes tools for fetching and analyzing news articles using rule-based NLP methods like VADER and spaCy.

---

# Features

- Fetch articles from NewsAPI
- Analyze sentiment using VADER
- Filter by S&P 500 tickers

---

# Installation

```bash
pip install yufrosine

# Usage
from yufrosine import main
main.run_analysis()
