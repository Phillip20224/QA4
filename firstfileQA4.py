from dotenv import load_dotenv
import os

load_dotenv()  # Load variables from .env

# Access them
openai_key = os.getenv("open_ai_key")
nyt_key = os.getenv("nytimes_api_key")
guardian_key = os.getenv("guardian_api_key")

import requests

# Fetch from NYT
def fetch_nyt():
    url = 'https://api.nytimes.com/svc/topstories/v2/home.json'
    params = {'api-key': nyt_key}
    response = requests.get(url, params=params)
    articles = response.json().get('results', [])

    print("\n🗞️ New York Times Top Stories:")
    for article in articles[:3]:  # Limit to top 3
        print(f"- {article['title']}\n  Link: {article['url']}\n")

# Fetch from The Guardian
def fetch_guardian():
    url = 'https://content.guardianapis.com/search'
    params = {
        'api-key': guardian_key,
        'show-fields': 'headline',
        'page-size': 3
    }
    response = requests.get(url, params=params)
    articles = response.json().get('response', {}).get('results', [])

    print("\n📰 The Guardian Headlines:")
    for article in articles:
        print(f"- {article['webTitle']}\n  Link: {article['webUrl']}\n")

# Run both
fetch_nyt()
fetch_guardian()

import openai
