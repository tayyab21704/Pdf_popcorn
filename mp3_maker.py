import requests
import os

API_KEY = "sk_e5e552b1dc870707e9182bff0c864b9be2b485a5b6ef06e7"  # Replace with your actual API key

# Set Voice IDs (Male & Female)
MALE_VOICE_ID = "CwhRBWXzGAHq8TQ4Fs17"  # Roger voice id
FEMALE_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Rachel voice id

def text_to_speech(text, voice_id, index):
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
        file_name = f"segment_{index}.mp3"
        with open(file_name, "wb") as audio_file:
            audio_file.write(response.content)
        print(f"Saved: {file_name}")
        return True
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return False

def create_podcast_segments(lines):
    # Process the script into lines
    # lines = [line.split(": ", 1)[1] if ": " in line else line 
    #         for line in script_text.strip().split("\n") 
    #         if line.strip()]
    
    voice_ids = [MALE_VOICE_ID, FEMALE_VOICE_ID]
    
    # Generate audio segments
    for i, line in enumerate(lines):
        voice_id = voice_ids[i % 2]
        if not text_to_speech(line, voice_id, i):
            return False
    
    print("All podcast segments generated!")
    return True

def merge_segments(num_segments, output_filename="final_podcast.mp3"):
    try:
        # Import here to avoid initial import issues
        from pydub import AudioSegment
        
        # Get all generated MP3 segments
        audio_segments = []
        for i in range(num_segments):
            file_name = f"segment_{i}.mp3"
            if os.path.exists(file_name):
                audio_segments.append(AudioSegment.from_mp3(file_name))

        # Merge all segments
        if audio_segments:
            final_audio = sum(audio_segments)  # Concatenates all MP3 files
            final_audio.export(output_filename, format="mp3")
            print(f"Final podcast saved as {output_filename}")
            
            # Clean up segment files
            for i in range(num_segments):
                segment_file = f"segment_{i}.mp3"
                if os.path.exists(segment_file):
                    os.remove(segment_file)
            return True
        else:
            print("No audio segments found to merge.")
            return False
            
    except ImportError:
        print("Could not import pydub. Using alternative method...")
        try:
            with open(output_filename, 'wb') as outfile:
                for i in range(num_segments):
                    segment_file = f"segment_{i}.mp3"
                    if os.path.exists(segment_file):
                        with open(segment_file, 'rb') as infile:
                            outfile.write(infile.read())
                        os.remove(segment_file)
                print(f"Final podcast saved as {output_filename}")
                return True
        except Exception as e:
            print(f"Error creating final podcast: {str(e)}")
            return False


def create_podcast(script_text, output_filename="final_podcast.mp3"):
    """Main function to create a podcast from script text."""
    # First create all the audio segments
    if create_podcast_segments(script_text):
        # Count the number of lines for merging
        num_segments = len([line for line in script_text.strip().split("\n") if line.strip()])
        # Then merge them into the final podcast
        return merge_segments(num_segments, output_filename)
    return False