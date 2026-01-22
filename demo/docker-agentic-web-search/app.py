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
import numpy as np
import pandas as pd

from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.layers import Dropout
from tensorflow.keras.optimizers import Adam
OLLAMA_HOST = "http://host.docker.internal:11434"
ALERT_RULES = {
    "sentiment_threshold": 0.6,
    "price_move_pct": 0.01,
    "time_window_hours": 24
}

def RSI(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(period).mean()
    loss = -delta.where(delta < 0, 0).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def MACD(series, fast=12, slow=26, signal=9):
    ema_fast = series.ewm(span=fast).mean()
    ema_slow = series.ewm(span=slow).mean()
    macd = ema_fast - ema_slow
    signal_line = macd.ewm(span=signal).mean()
    return macd, signal_line



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
    
def get_stock_data(symbol: str, days: int = 2):
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period=f"{days}d",interval="5m")

    if hist.empty:
        return []

    return hist
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

def predict_inference(topic, symbol):
    price_move = 0.0
    data = get_stock_data(symbol, days=60)
    

    data["RSI"] = RSI(data["Close"])
    data["MACD"], data["MACD_SIGNAL"] = MACD(data["Close"])
    data.dropna(inplace=True)

    features = data[["Close", "RSI", "MACD", "MACD_SIGNAL"]].values
    
    feature_scaler = MinMaxScaler()
    scaled = feature_scaler.fit_transform(features)

    X, y = [], []
    window = 30   # 30 candles = ~150 minutes

    for i in range(window, len(scaled)):
        X.append(scaled[i-window:i])
        y.append(scaled[i, 0])   # predict Close price

    X = np.array(X)
    y = np.array(y)

    #print("X shape:", X.shape)  # (samples, window, features)
    split = int(0.8 * len(X))
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]

    model = Sequential([
        LSTM(64, return_sequences=True, input_shape=(window, X.shape[2])),
        Dropout(0.2),
        LSTM(64),
        Dropout(0.2),
        Dense(1)
    ])
    optimizer = Adam(
        learning_rate=5e-5,
        clipnorm=1.0
    )

    model.compile(optimizer=optimizer, loss="mse")

    #model.compile(optimizer="adam", loss="mse")
    model.fit(X_train, y_train, epochs=8, batch_size=32)

    predicted = model.predict(X_test)

    # inverse scale CLOSE only
    #close_scaler = MinMaxScaler()
    feature_scaler.fit(data[["Close"]])

    predicted_price = feature_scaler.inverse_transform(predicted)
    actual_price = feature_scaler.inverse_transform(y_test.reshape(-1, 1))

    last_close = actual_price[-1][0]
    next_close = predicted_price[-1][0]
    price_move = next_close
    print(price_move)
    change_pct = (next_close - last_close) / last_close
    if change_pct > 0.003:
        signal = "BUY 📈"
    elif change_pct < -0.003:
        signal = "SELL 📉"
    else:
        signal = "HOLD ⚖️"

    return True, {
		"signal": signal,
        "price_move": change_pct,
        "predicted_price":price_move
    }
        
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
    price_from_news = meta['price_move']
    triggerr, peta = predict_inference(topic,symbol)
    price_from_price_sequence_predicton = peta['price_move']
	
    price = price_from_news + price_from_price_sequence_predicton
    if price > 0:
        price = price/2
    if not trigger:
        return jsonify({"status": "no alert"})
    if not triggerr:
        return jsonify({"status": "no alert"})
    
    explanation = alert_explainer(meta)

    alert_msg = f"""
NEWS-DRIVEN STOCK ALERT
Company: {topic}
Symbol: {symbol}
Sentiment: {meta['sentiment']:.2f}
Price Move: {price:.2f}%
Signal: {peta['signal']}
Predicted from News: {price_from_news:.2f}
Predicted from Model: {price_from_price_sequence_predicton:.2f}
Predicted price: {peta['predicted_price']:.2f} /- INR
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
            store_document(item["body"],topic=keyword, published_at = datetime.fromisoformat(item["date"].replace("Z", "+00:00")))
            stored += 1

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
