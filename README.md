# 📰 Brewspaper
Brewspaper is a personalized news proof-of-concept app that fetches and summarizes relevant news articles based on any topic the user enters.

It uses RSS feeds, language models, and embeddings to retrieve, vectorize, and rank articles most relevant to your interest — all in one simple UI powered by Streamlit.

# 🧪 How it works
Feeds are loaded from a JSON file (feeds.json)
Articles are parsed using feedparser + newspaper
Content is embedded with HuggingFace Embedding model
Chroma stores the embeddings locally (in a folder called Chroma)
When a user enters a topic, filter to top 30 news with highest cosine similarity (RAG)
Relevant articles are retrieved and then passed to Gemini
Gemini selects the top 3 most relevant news pieces and summarizes them

# 🛠️ Setup
1. Clone the repository  
`git clone https://github.com/ChinnapatRuji/brewspaper.git`

3. Set up the Environment File  
Copy the example file and fill in your details:  
`cp .env.example .env`  
Then open `.env` and add your API keys or model names.

5. Download Dependencies  
Ensure you have Python 3.9+ installed. All required Python packages are listed in 'requirements.txt'.  
To install them, run: `pip install -r requirements.txt`

7. Run the streamlit app:  
`streamlit run app.py`
