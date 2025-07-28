import feedparser
import pandas as pd
import json
from newspaper import Article
import google.generativeai as genai

def get_news_sources(file, output_file='news_articles.csv'):
    with open(file, 'r') as f:
        rss_data = json.load(f)

    entries = []
    for source, data in rss_data.items():
        for url in data['rss']:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                entry_title = entry.get('title', '')
                entry_link = entry.get('link', '')
                published = entry.get('published', '')
                summary = entry.get('summary', '')
                full_content = ''
                if entry_link:
                    try:
                        article = Article(entry_link)
                        article.download()
                        article.parse()
                        full_content = article.text
                    except Exception as e:
                        print(f"Error fetching article from {entry_link}: {e}")
                        full_content = summary

                entries.append({
                    'source': source,
                    'title': entry_title,
                    'link': entry_link,
                    'published': published,
                    'summary': summary,
                    'content': full_content
                })

    df = pd.DataFrame(entries)
    df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"Saved {len(df)} articles to {output_file}")

def ask_gemini_to_pick_best_source(df, target_topic):
    articles = df
    prompt = f"Topic: {target_topic}\n\n"
    prompt += "Below are news articles from different sources.\n\n"
    prompt += "Articles:\n"

    for i, row in articles.iterrows():
        entry_link = row.get('link', 'N/A')
        published_date = row.get('published', 'N/A')
        snippet_raw = row.get('content')
        if not isinstance(snippet_raw, str) or pd.isna(snippet_raw):
            snippet_raw = row.get('summary')
        if not isinstance(snippet_raw, str) or pd.isna(snippet_raw):
            snippet_raw = ''
        snippet = str(snippet_raw)[:300].replace('...\n', ' ')
        
        prompt += f"--- Article {i+1} ---\n"
        prompt += f"Source: {row['source']}\n"
        prompt += f"Title: {row['title']}\n"
        prompt += f"Link: {entry_link}\n"
        prompt += f"Published: {published_date}\n"
        prompt += f"Content: {snippet}\n\n"

    prompt += (
        "From all these articles, choose the ONLY top 3 most relevant news article with criteria such as popularity,"
        "connection to topic, significance, unbias. I want ONLY the most recent news\n"
    )
    prompt += (
        "Respond with:\n"
        "- A relevance rating for articles (1-5) with source names, news article title, "
        "quick summary and its relevance to topic strictly in the following format\n"
        "\nFormat:\n"
        "1. SourceName - Title\n'Rating:' rating\n Relevance: \n Published date:\n Link: \n"
        "1. SourceName - Title\n'Rating:' rating\n Relevance: \n Published date:\n Link: \n"
        "1. SourceName - Title\n'Rating:' rating\n Relevance: \n Published date:\n Link: \n"
        "Note: ONLY shows 3 news article"
        "if not news is relevant. Say that no news is relevant to the topic"
    )

    genai.configure(api_key="AIzaSyBiJbkFABKwtZ-RZJmudvH9O2YfoZDe7pA")
    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content(prompt)
    return response.text

def get_news(topic):
    df = pd.read_csv('news_articles.csv')
    response = ask_gemini_to_pick_best_source(df, topic)
    return response


def main():
    print("1. Create New News File\n2. Get News")
    to_do = input("Input (1 or 2): ").strip()
    if to_do == "1":
        get_news_sources('feeds.json')
    elif to_do == "2":
        topic = input("Enter topic of interest: ").strip()
        #topic = "Things that can affect TCP Group in Thailand"
        result = get_news(topic)
        print("\nTop Relevant News Articles:\n")
        
        print(result)
    else:
        print("Invalid option. Please enter 1 or 2.")

if __name__ == "__main__":
    main()
