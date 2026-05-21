"""
install_models.py — Download XTTS-v2 model (one-time setup, runs offline after)
"""
import sys
import subprocess

def run(cmd):
    print(f"\n▶ {cmd}")
    result = subprocess.run(cmd, shell=True)
    return result.returncode == 0

print("=" * 60)
print("  VoiceLab — AI Voice Generator Model Installer")
print("=" * 60)
print("\nThis will download the XTTS-v2 voice cloning model (~2GB).")
print("After download, everything runs 100% OFFLINE.\n")

print("📦 Installing Python packages...")
packages = [
    "flask",
    "flask-cors",
    "TTS",
    "soundfile",
    "numpy",
]

for pkg in packages:
    if not run(f"{sys.executable} -m pip install {pkg}"):
        print(f"⚠️  Warning: {pkg} may have had issues")

print("\n🤖 Pre-downloading XTTS-v2 model (voice cloning)...")
try:
    from TTS.api import TTS
    print("Downloading tts_models/multilingual/multi-dataset/xtts_v2 ...")
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=False)
    print("\n✅ XTTS-v2 downloaded! Voice cloning is ready.")
except Exception as e:
    print(f"\n⚠️  XTTS-v2 download failed: {e}")
    print("Trying fallback model (no voice cloning)...")
    try:
        from TTS.api import TTS
        tts = TTS("tts_models/en/ljspeech/tacotron2-DDC", gpu=False)
        print("✅ Fallback TTS model ready!")
    except Exception as e2:
        print(f"❌ Fallback also failed: {e2}")

print("\n" + "=" * 60)
print("  ✅ Setup Complete! Now run: python app.py")
print("  Then open: http://localhost:5050")
print("=" * 60 + "\n")