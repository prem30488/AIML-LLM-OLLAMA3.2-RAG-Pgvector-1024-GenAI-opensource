from flask import Flask, request, jsonify
from PIL import Image
import io
import torch
from transformers import BlipProcessor, BlipForConditionalGeneration
from paddleocr import PaddleOCR

app = Flask(__name__)

# ---------------------------------------
# Load BLIP Model for Image Captioning
# ---------------------------------------
caption_processor = BlipProcessor.from_pretrained(
    "/app/models/blipbase",
    local_files_only=True
)
caption_model = BlipForConditionalGeneration.from_pretrained(
    "/app/models/blipbase",
    local_files_only=True
)
caption_model.eval()

# ---------------------------------------
# Load OCR Model
# ---------------------------------------
ocr = PaddleOCR(lang="en")


# ================================
# 1️⃣ IMAGE CAPTIONING ENDPOINT
# ================================
@app.post("/caption")
def caption():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    img_file = request.files["image"]
    img = Image.open(io.BytesIO(img_file.read())).convert("RGB")

    inputs = caption_processor(img, return_tensors="pt")
    output = caption_model.generate(**inputs)
    caption_text = caption_processor.decode(output[0], skip_special_tokens=True)

    return jsonify({"caption": caption_text})


# ================================
# 2️⃣ OCR ENDPOINT
# ================================
@app.post("/ocr")
def ocr_api():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    img_file = request.files["image"]
    img_bytes = img_file.read()

    result = ocr.ocr(img_bytes)

    lines = []
    for line in result:
        for text in line:
            lines.append(text[1][0])

    return jsonify({"ocr_text": "\n".join(lines)})


# ================================
# Server
# ================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8002)