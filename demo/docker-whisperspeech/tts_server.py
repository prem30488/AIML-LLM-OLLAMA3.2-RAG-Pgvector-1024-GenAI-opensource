import torch
import torchaudio
import io
from flask import Flask, request, send_file, jsonify, Response
from whisperspeech.pipeline import Pipeline


app = Flask(__name__)

pipe = Pipeline(
    s2a_ref="collabora/whisperspeech:s2a-q4-tiny-en+pl.model",
    torch_compile=False
)

@app.route("/tts", methods=["POST"])
def tts():
    data = request.get_json()
    if not data or "text" not in data:
        return {"error": "Missing 'text'"}, 400
    if not data or "voice" not in data:
        return {"error": "Missing 'voice'"}, 400
    
  #if pipe is None:
   #     return jsonify({"error": "TTS service unavailable."}), 503
    # 1. Look up the speaker ID (as previously discussed)
    speaker_name = data.get("voice", 'ljspeech')
    speaker_id =  0 # Fallback to 0 if name is unknown
    speakers = torch.tensor(speaker_id)
    pipe.s2a.eval()
    
    with torch.no_grad():
        try:
            waveform = pipe.generate(data["text"])
            buffer = io.BytesIO()
            if waveform.dim() == 1:
                waveform = waveform.unsqueeze(0)
            
            torchaudio.save(
              buffer,
              waveform,
              24000,
              format="wav"
            )
            audio_bytes = buffer.getvalue()
            # ... handle response ...
            response = Response(
                audio_bytes,
                mimetype="audio/wav"
            )
            response.headers['Content-Disposition'] = 'attachment; filename=speech.wav'
            return response
        except Exception as e:
            return jsonify({"error": f"TTS generation failed: {e}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
