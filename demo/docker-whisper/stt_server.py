from flask import Flask, request, jsonify
from faster_whisper import WhisperModel
import uuid, os

app = Flask(__name__)

model = WhisperModel(
    "base",
    device="cpu",        # change to "cuda" if GPU
    compute_type="int8"
)

UPLOAD_DIR = "/tmp"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.route("/transcribe", methods=["POST"])
def transcribe():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file"}), 400

    audio = request.files["audio"]
    file_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}.wav")
    audio.save(file_path)

    segments, info = model.transcribe(file_path)

    text = " ".join(segment.text for segment in segments)

    return jsonify({
        "language": info.language,
        "confidence": info.language_probability,
        "text": text
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8006)
