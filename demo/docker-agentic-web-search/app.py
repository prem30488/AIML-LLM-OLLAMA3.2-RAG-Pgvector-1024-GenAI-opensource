from flask import Flask, request, jsonify
from sqlalchemy.orm import Session
import requests
from bs4 import BeautifulSoup

from phi.agent import Agent
from phi.tools.duckduckgo import DuckDuckGo
from phi.model.ollama import Ollama
from phi.embedder.ollama import OllamaEmbedder

from db import SessionLocal, Document

from duckduckgo_search import DDGS

import yfinance as yf
from datetime import datetime, timedelta


OLLAMA_HOST = "http://host.docker.internal:11434"  # change to localhost if not docker
NEWS_DOMAINS = (
	"www.msn.com",
    "thehindu.com",
    "indianexpress.com",
    "hindustantimes.com",
    "timesofindia.indiatimes.com",
    "livemint.com",
    "economictimes.indiatimes.com",
    "business-standard.com",
    "moneycontrol.com",
    "financialexpress.com",
    "ndtv.com",
    "news18.com",
    "scroll.in",
    "thewire.in",
    "reuters.com",
    "bbc.com",
    "bloomberg.com",
)
ALERT_RULES = {
    "sentiment_threshold": 0.6,
    "price_move_pct": 0.01,     # % move
    "time_window_hours": 24
}

def domain_query(keyword: str) -> str:
    domain_filters = " OR ".join(f"site:{d}" for d in NEWS_DOMAINS)
    return f"{keyword} ({domain_filters})"

def detect_sentiment_spike(topic):
    since = datetime.utcnow() - timedelta(hours=24)

    db = SessionLocal()
    docms = (
        db.query(Document)
        .filter(Document.topic == topic)
        #.filter(Document.published_at >= since)
        .all()
    )
    db.close()
    print(docms)
    if not docms:
        return None

    avg_sentiment = sum(d.sentiment for d in docms) / len(docms)
    return avg_sentiment


def get_stock_prices(symbol: str, days: int = 2):
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period=f"{days}d")

    if hist.empty:
        return []

    return hist["Close"].tolist()
def percent_change(old_price: float, new_price: float) -> float:
    if old_price == 0:
        return 0.0

    return ((new_price - old_price) / old_price) * 100

def detect_price_movement(symbol: str, threshold: float = 0.03):
    prices = get_stock_prices(symbol, days=2)
    # prices = [day1_close, day2_close]

    if not prices or len(prices) < 2:
        return 0.0

    previous_close = prices[-2]
    latest_close = prices[-1]

    if previous_close == 0:
        return 0.0

    return percent_change(previous_close,latest_close)

def should_alert(topic, symbol):
    sentiment = detect_sentiment_spike(topic)
    price_move = detect_price_movement(symbol)
    print(sentiment)
    print(price_move)
    if sentiment is None:
        return False, None
    else:
        return True, {
            "sentiment": sentiment,
            "price_move": price_move
        }

def alert_explainer(data):
    agent = Agent(
        model=Ollama(model="llama3.2", temperature=0,host=OLLAMA_HOST),
        instructions=[
            "Explain why this alert was triggered.",
            "Use financial language.",
            "Be concise.",
            f"DATA:\n{data}"
        ]
    )
    return agent.run("Explain alert").content


app = Flask(__name__)

@app.route("/run-alerts", methods=["POST"])
def run_alerts():
    data = request.json
    topic = data["topic"]
    symbol = data["symbol"]

    trigger, meta = should_alert(topic, symbol)

    if not trigger:
        return jsonify({"status": "no alert"})

    explanation = alert_explainer(meta)

    alert_msg = f"""
NEWS-DRIVEN STOCK ALERT
Company: {topic}
Symbol: {symbol}
Sentiment: {meta['sentiment']:.2f}
Price Move: {meta['price_move']:.2f}%

Reason:
{explanation}
"""

    #send_slack_alert(alert_msg)

    return jsonify({
        "status": "alert_sent",
        "details": alert_msg
    })


# =========================
# Embeddings
# =========================
embedder = OllamaEmbedder(
    model="nomic-embed-text",
    host=OLLAMA_HOST
)
sentiment_agent = Agent(
    model=Ollama(
        model="llama3.2",
        temperature=0.0,          # deterministic
        host=OLLAMA_HOST
    ),
    instructions=[
        "You are a sentiment analysis engine.",
        "Analyze the sentiment of the given text.",
        "Return ONLY a single number between -1 and 1.",
        "-1 = very negative",
        "0 = neutral",
        "1 = very positive",
        "Do NOT explain anything.",
        "Do NOT add text.",
    ],
)
# =========================
# DB helpers
# =========================
def detect_sentiment(text: str) -> float:
    prompt = f"""
    Classify the sentiment of the following news text.
    Respond with ONLY a number between -1 and 1.

    Text:
    {text}
    """

    response = sentiment_agent.run(prompt)
    try:
        return float(response.content.strip())
    except Exception:
        return 0.0


def store_document(text: str, topic: str,published_at: datetime | None = None):
    embedding = embedder.get_embedding(text)
    sentiment = detect_sentiment(text) 
    t=topic
    print(t)
    db: Session = SessionLocal()
    db.add(Document(content=text, embedding=embedding, sentiment=sentiment,published_at=published_at or datetime.utcnow(),topic=t))
    db.commit()
    db.close()

def retrieve_documents(query: str, limit=3):
    query_embedding = embedder.get_embedding(query)
    db: Session = SessionLocal()
    docs = (
        db.query(Document)
        .order_by(Document.embedding.l2_distance(query_embedding))
        .limit(limit)
        .all()
    )
    db.close()
    return [d.content for d in docs]

# =========================
# Simple HTML Scraper
# =========================
def scrape_url(url: str) -> str:
    try:
        r = requests.get(url, timeout=10, headers={
            "User-Agent": "Mozilla/5.0"
        })
        soup = BeautifulSoup(r.text, "html.parser")
        return soup.get_text(separator=" ", strip=True)
    except Exception:
        return ""

# =========================
# INGEST ENDPOINT
# =========================
@app.route("/ingest", methods=["GET"])
def ingest():
    keyword = request.args.get("keyword")
    if not keyword:
        return jsonify({"error": "keyword required"}), 400

    search_agent = Agent(
        model=Ollama(model="llama3.2", host=OLLAMA_HOST),
        tools=[DuckDuckGo()],
        instructions=[
            "Search ONLY news websites.",
            "Search ONLY articles from the last 24 hours.",
            "Return ONLY URLs.",
            "One URL per line.",
            "No explanations."
        ]
    )
    sample = DDGS().news(
            keywords=keyword,
            region="in-en",
            safesearch="off",
            timelimit="d",
            max_results=10
            )
    print(sample)

    urls = [item["url"] for item in sample]
    bodies = [item["body"] for item in sample]

    stored = 0
    for item in sample:
        if len(item["body"]) > 50:
            store_document(item["body"],topic=keyword, published_at = datetime.fromisoformat(item["date"].replace("Z", "+00:00"))
)
            stored += 1

    #query = domain_query(keyword)

    #result = search_agent.run(query)

    #urls = [
	#    line.strip()
	#    for line in result.content.url
	#    if line.startswith("https")
	    #and any(domain in line for domain in NEWS_DOMAINS)
    #]

    #stored = 0
    #for url in urls[:5]:
    #    text = scrape_url(url)
    #    if len(text) > 500:
    #        store_document(text)
    #        stored += 1

    return jsonify({
        "status": "ingested",
        "keyword": keyword,
        "urls_found": len(urls),
        "documents_stored": stored,
        "bodies": bodies,
        "urls": urls
    })

# =========================
# RAG QUERY
# =========================
@app.route("/rag-query", methods=["POST"])
def rag_query():
    question = request.json.get("question")
    if not question:
        return jsonify({"error": "question required"}), 400

    context = retrieve_documents(question)

    


    return jsonify({
        "question": question,
        "answer": answer.content,
        "sources": context
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8008)
