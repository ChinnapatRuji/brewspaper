import feedparser   
import pandas as pd
import json
from newspaper import Article
import google.generativeai as genai
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import os
from dotenv import load_dotenv

load_dotenv()
CHROMA_PATH = "chroma"
embedding_model_name = os.getenv("HF_EMBEDDING_MODEL")
embedding_model = HuggingFaceEmbeddings(model_name=embedding_model_name)

def get_news(file):
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
    return df

def get_vector(df):
    chunks = [
        f"Source: {row['source']}\nTitle: {row['title']}\nPublished: {row['published']}\nSummary: {row['summary']}\nContent: {row['content']}\nLink: {row['link']}"
        for _, row in df.iterrows()
    ]
    vector_db = Chroma.from_texts(
        texts=chunks,
        embedding=embedding_model,
        collection_name="news_collection"
    )
    return vector_db


def get_context(vector_db, query, k=30):
    docs = vector_db.similarity_search(query, k=k)
    context = "\n\n".join([clean_text(doc.page_content) for doc in docs])
    return context

def clean_text(text):
    return text.strip().replace("\n", " ")

def ask_gemini_pick_best_news(context, query):
    prompt = ( 
        f"Topic: {query}\n\n"
        f"Below are news articles from different sources.\n\n"
        f"Articles:\n{context} \n\n"
    )

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
        "Note: ONLY shows 3 news article\n"
        "if not news is relevant. Say that no news is relevant to the topic"
    )

    genai.configure(api_key="AIzaSyBiJbkFABKwtZ-RZJmudvH9O2YfoZDe7pA")
    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content(prompt)
    return response.text