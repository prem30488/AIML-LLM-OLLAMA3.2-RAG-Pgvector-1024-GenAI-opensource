from flask import Flask, request, send_file, jsonify
from ultralytics import YOLO
import cv2
import numpy as np
import io
from PIL import Image

app = Flask(__name__)

model = YOLO("./models/yolo/yolo11m.pt")

@app.post("/detect")
def detect_objects():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    # Read image
    file = request.files["image"]
    image = Image.open(file.stream).convert("RGB")
    img_np = np.array(image)

    # Run inference
    results = model(img_np)

    # Draw detections
    annotated_img = img_np.copy()
    for r in results:
        boxes = r.boxes
        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])

            label = f"{model.names[cls_id]} {conf:.2f}"

            # Draw bounding box
            cv2.rectangle(annotated_img, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # Draw label
            cv2.putText(
                annotated_img,
                label,
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2
            )

    # Convert to image bytes
    output_img = Image.fromarray(annotated_img)
    img_io = io.BytesIO()
    output_img.save(img_io, format="JPEG")
    img_io.seek(0)

    return send_file(img_io, mimetype="image/jpeg")
# ================================
# Server
# ================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8003)