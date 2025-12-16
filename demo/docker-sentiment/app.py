from flask import Flask, request, send_file, jsonify, Response
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score

# Sample data
data = {
    "text": [
        "I love this product",
        "This is the worst service ever",
        "Amazing experience",
        "Not happy with the quality",
        "Very satisfied with support",
        "Terrible and disappointing",
        "That was ok",
        "Not so good not so bad",
        "It will work"
    ],
    "sentiment": ["positive", "negative", "positive", "negative", "positive", "negative","neutral", "neutral", "neutral"]
}

df = pd.DataFrame(data)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    df["text"], df["sentiment"], test_size=0.2, random_state=42
)

# Pipeline
model = Pipeline([
    ("tfidf", TfidfVectorizer(stop_words="english")),
    ("clf", LogisticRegression())
])

# Train
model.fit(X_train, y_train)

# Predict
predictions = model.predict(X_test)

print("Accuracy:", accuracy_score(y_test, predictions))


app = Flask(__name__)

# ================================
# 1️⃣ IMAGE CAPTIONING ENDPOINT
# ================================
@app.post("/sentiment")
def sentiment():
    data = request.get_json()
    if not data or "text" not in data:
        return {"error": "Missing 'text'"}, 400

    text = data["text"]

    # sklearn expects List[str], not str
    sentiment = model.predict([text])[0]

    print("Prediction:", sentiment)

    return jsonify({"sentiment": sentiment})



# ================================
# Server
# ================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8004)