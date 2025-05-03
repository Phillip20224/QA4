from dotenv import load_dotenv
import os
import requests
from openai import OpenAI

# Load environment variables from .env
load_dotenv()
openai_key = os.getenv("open_ai_key")
nyt_key = os.getenv("nytimes_api_key")
guardian_key = os.getenv("guardian_api_key")

sender_email = os.getenv("sender_email")
recipient_email = os.getenv("recipient_email")
email_password = os.getenv("email_password")


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

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def create_email_content(all_articles):
    body = ""
    for source, articles in all_articles.items():
        body += f"\n=== {source} ===\n\n"
        for article in articles:
            body += f"{article['title']}\n{article['url']}\nSummary: {article['summary']}\n\n"
    return body

def send_email(subject, body, sender_email, recipient_email, smtp_server, smtp_port, login, password):
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))  # Or 'html' for HTML content

    with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
        server.login(login, password)
        server.send_message(msg)
        print("✅ Email sent successfully.")

# Example usage in your main block
if __name__ == "__main__":
    nyt_articles = fetch_nyt()
    guardian_articles = fetch_guardian()

    # Summarize and attach summaries
    for article in nyt_articles:
        full_text = f"{article['title']}\n\n{article['abstract']}"
        article['summary'] = summarize_text(full_text)

    for article in guardian_articles:
        full_text = f"{article['title']}\n\n{article['abstract']}"
        article['summary'] = summarize_text(full_text)

    all_articles = {
        "The New York Times": nyt_articles,
        "The Guardian": guardian_articles
    }

    email_body = create_email_content(all_articles)

send_email(
    subject="🗞️ Daily News Summaries",
    body=email_body,
    sender_email=sender_email,
    recipient_email=recipient_email,
    smtp_server="smtp.gmail.com",
    smtp_port=465,
    login=sender_email,
    password=email_password
)
