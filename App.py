"""
AI Voice Generator - Offline Local App
Uses: Coqui TTS for text-to-speech and voice cloning
"""

from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import os
import uuid
import json
import numpy as np
import soundfile as sf
import tempfile

app = Flask(__name__, static_folder="static")
CORS(app)

OUTPUT_DIR = "outputs"
VOICE_DIR = "voices"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(VOICE_DIR, exist_ok=True)

tts_engine = None
AVAILABLE_VOICES = {}

def load_tts():
    global tts_engine
    try:
        from TTS.api import TTS
        # Use XTTS-v2 for voice cloning support (runs fully offline after first download)
        tts_engine = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=False)
        print("✅ XTTS-v2 loaded successfully (supports voice cloning!)")
        return True
    except Exception as e:
        print(f"⚠️  XTTS-v2 not available: {e}")
        try:
            from TTS.api import TTS
            tts_engine = TTS("tts_models/en/ljspeech/tacotron2-DDC", gpu=False)
            print("✅ Fallback TTS model loaded")
            return True
        except Exception as e2:
            print(f"❌ TTS load failed: {e2}")
            return False

def scan_voices():
    """Scan voice samples directory"""
    global AVAILABLE_VOICES
    AVAILABLE_VOICES = {}
    if os.path.exists(VOICE_DIR):
        for f in os.listdir(VOICE_DIR):
            if f.endswith((".wav", ".mp3", ".flac")):
                name = os.path.splitext(f)[0]
                AVAILABLE_VOICES[name] = os.path.join(VOICE_DIR, f)
    return AVAILABLE_VOICES

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/api/status")
def status():
    scan_voices()
    model_name = "Not loaded"
    if tts_engine:
        try:
            model_name = str(tts_engine.model_name)
        except:
            model_name = "Loaded"
    return jsonify({
        "tts_loaded": tts_engine is not None,
        "model": model_name,
        "voices": list(AVAILABLE_VOICES.keys()),
        "voice_cloning": "xtts" in model_name.lower() if tts_engine else False
    })

@app.route("/api/synthesize", methods=["POST"])
def synthesize():
    if not tts_engine:
        return jsonify({"error": "TTS engine not loaded. Run: python install_models.py"}), 503

    data = request.json
    text = data.get("text", "").strip()
    voice_name = data.get("voice", None)
    language = data.get("language", "en")
    speed = float(data.get("speed", 1.0))

    if not text:
        return jsonify({"error": "No text provided"}), 400

    output_filename = f"{uuid.uuid4()}.wav"
    output_path = os.path.join(OUTPUT_DIR, output_filename)

    try:
        scan_voices()
        speaker_wav = None
        if voice_name and voice_name in AVAILABLE_VOICES:
            speaker_wav = AVAILABLE_VOICES[voice_name]

        model_name = str(tts_engine.model_name) if tts_engine else ""

        if "xtts" in model_name.lower():
            if speaker_wav:
                tts_engine.tts_to_file(
                    text=text,
                    speaker_wav=speaker_wav,
                    language=language,
                    file_path=output_path
                )
            else:
                # Use default speaker for XTTS
                speakers = tts_engine.speakers if hasattr(tts_engine, 'speakers') and tts_engine.speakers else None
                if speakers:
                    tts_engine.tts_to_file(
                        text=text,
                        speaker=speakers[0],
                        language=language,
                        file_path=output_path
                    )
                else:
                    tts_engine.tts_to_file(text=text, file_path=output_path)
        else:
            tts_engine.tts_to_file(text=text, file_path=output_path)

        # Apply speed change if needed
        if speed != 1.0:
            try:
                import librosa
                audio, sr = librosa.load(output_path, sr=None)
                audio_stretched = librosa.effects.time_stretch(audio, rate=speed)
                sf.write(output_path, audio_stretched, sr)
            except ImportError:
                pass  # Skip speed if librosa not available

        return jsonify({
            "success": True,
            "file": output_filename,
            "url": f"/api/audio/{output_filename}"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/audio/<filename>")
def get_audio(filename):
    path = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(path):
        return send_file(path, mimetype="audio/wav")
    return jsonify({"error": "File not found"}), 404

@app.route("/api/upload_voice", methods=["POST"])
def upload_voice():
    """Upload a voice sample for cloning"""
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    name = request.form.get("name", "my_voice").strip().replace(" ", "_")

    if not file.filename.endswith((".wav", ".mp3", ".flac")):
        return jsonify({"error": "Only .wav, .mp3, .flac files supported"}), 400

    save_path = os.path.join(VOICE_DIR, f"{name}.wav")

    # Convert to wav if needed
    if file.filename.endswith(".wav"):
        file.save(save_path)
    else:
        with tempfile.NamedTemporaryFile(suffix=os.path.splitext(file.filename)[1], delete=False) as tmp:
            file.save(tmp.name)
            try:
                import librosa
                audio, sr = librosa.load(tmp.name, sr=22050)
                sf.write(save_path, audio, sr)
            except:
                file.save(save_path)
            os.unlink(tmp.name)

    scan_voices()
    return jsonify({"success": True, "voice": name, "voices": list(AVAILABLE_VOICES.keys())})

@app.route("/api/delete_voice/<name>", methods=["DELETE"])
def delete_voice(name):
    path = os.path.join(VOICE_DIR, f"{name}.wav")
    if os.path.exists(path):
        os.remove(path)
        scan_voices()
        return jsonify({"success": True})
    return jsonify({"error": "Voice not found"}), 404

@app.route("/api/voices")
def list_voices():
    scan_voices()
    return jsonify({"voices": list(AVAILABLE_VOICES.keys())})

if __name__ == "__main__":
    print("🎙️  AI Voice Generator - Loading TTS Engine...")
    load_tts()
    port = int(os.environ.get("PORT", 5050))
    print(f"🌐 Starting server at http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)