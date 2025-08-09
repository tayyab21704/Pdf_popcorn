import requests
import os
import re
from io import BytesIO
from pydub import AudioSegment
from dotenv import load_dotenv

# ✅ Load environment variables from the custom .env file
load_dotenv(dotenv_path="rqmnts.env")

# ✅ Fetch API Key securely
API_KEY = os.getenv("ELEVENLABS_API_KEY")

# ✅ ElevenLabs voice IDs
MALE_VOICE_ID = "CwhRBWXzGAHq8TQ4Fs17"      # Ryan
FEMALE_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"    # Sarah

def text_to_speech(text, voice_id):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "Content-Type": "application/json",
        "xi-api-key": API_KEY
    }
    data = {
        "text": text,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.8
        }
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return AudioSegment.from_file(BytesIO(response.content), format="mp3")
    else:
        print(f"❌ Error: {response.status_code}, {response.text}")
        return None

def create_final_podcast(script_text, output_path="final_podcast.mp3"):
    final_audio = AudioSegment.empty()
    lines = script_text.strip().split("\n")

    # ✅ Speaker-to-Voice Mapping
    speaker_map = {
        "ryan": MALE_VOICE_ID,
        "sarah": FEMALE_VOICE_ID
    }

    for i, line in enumerate(lines):
        match = re.match(r"^(Ryan|Sarah)\s*:\s*(.+)$", line.strip(), re.IGNORECASE)
        if match:
            speaker = match.group(1).strip().lower()
            text = match.group(2).strip()
            voice_id = speaker_map.get(speaker)
            if voice_id:
                segment = text_to_speech(text, voice_id)
                if segment:
                    final_audio += segment
                else:
                    print(f"⚠️ Failed to synthesize line {i+1}: {line}")
            else:
                print(f"⚠️ Unknown speaker: {speaker}")
        else:
            print(f"⛔ Invalid format at line {i+1}: {line}")

    final_audio.export(output_path, format="mp3")
    print(f"✅ Podcast saved at {output_path}")
    return output_path  # Required for integration with app.py

# 🔒 Uncomment if you want to test this file independently
# from tayyab.script import script
# create_final_podcast(script, "example_podcast.mp3")
