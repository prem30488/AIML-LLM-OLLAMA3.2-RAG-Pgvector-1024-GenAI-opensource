from flask import Flask, request, jsonify, Response
from io import BytesIO
import torch
from diffusers import DiffusionPipeline

# switch to "mps" for apple devices
pipe = DiffusionPipeline.from_pretrained(
    "/app/models/sd15",
    local_files_only=True
)
device = "cpu"
pipe.to(device)

app = Flask(__name__)

# ----------------------------
# Image Generation Endpoint
# ----------------------------
@app.post("/tti")
def generate_image():
    data = request.get_json()
    if not data or "text" not in data:
        return jsonify({"error": "text is required"}), 400

    prompt = data["text"]

    try:
        img = pipe(prompt=prompt,num_inference_steps=40,guidance_scale=4.5,).images[0]
        # Convert PIL → bytes
        img_bytes = BytesIO()
        img.save(img_bytes, format="JPEG")
        img_bytes.seek(0)
        
        response = Response(
                img_bytes,
                mimetype="image/jpeg"
            )
        response.headers['Content-Disposition'] = 'attachment; filename=generated.jpeg'
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.get("/")
def health():
    return {"status": "Stable Diffusion M Flask service running!"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001)
