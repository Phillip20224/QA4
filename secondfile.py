from dotenv import load_dotenv
import os
import requests
from openai import OpenAI

# Load environment variables from .env
load_dotenv()
openai_key = os.getenv("open_ai_key")
nyt_key = os.getenv("nytimes_api_key")
guardian_key = os.getenv("guardian_api_key")

# Initialize OpenAI client
client = OpenAI(api_key=openai_key)

# ---- Fetch Functions ----

def fetch_nyt():
    url = 'https://api.nytimes.com/svc/topstories/v2/home.json'
    params = {'api-key': nyt_key}
    response = requests.get(url, params=params)
    articles = response.json().get('results', [])
    return [{
        'title': article['title'],
        'abstract': article.get('abstract', ''),
        'url': article['url']
    } for article in articles[:3]]

def fetch_guardian():
    url = 'https://content.guardianapis.com/search'
    params = {
        'api-key': guardian_key,
        'show-fields': 'headline,trailText',
        'page-size': 3
    }
    response = requests.get(url, params=params)
    articles = response.json().get('response', {}).get('results', [])
    return [{
        'title': article['webTitle'],
        'abstract': article.get('fields', {}).get('trailText', ''),
        'url': article['webUrl']
    } for article in articles]

# ---- OpenAI Summarization ----

def summarize_text(text):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes news articles."},
                {"role": "user", "content": f"Summarize the following article:\n\n{text}"}
            ],
            temperature=0.5,
            max_tokens=200
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[Error summarizing: {e}]"

# ---- Summarize and Display ----

def summarize_articles(articles, source_name):
    print(f"\n📚 Summaries from {source_name}:\n")
    for article in articles:
        full_text = f"{article['title']}\n\n{article['abstract']}"
        summary = summarize_text(full_text)
        print(f"📰 {article['title']}\n🔗 {article['url']}\n📄 Summary: {summary}\n")

# ---- Main ----

if __name__ == "__main__":
    nyt_articles = fetch_nyt()
    guardian_articles = fetch_guardian()

    summarize_articles(nyt_articles, "The New York Times")
    summarize_articles(guardian_articles, "The Guardian")
