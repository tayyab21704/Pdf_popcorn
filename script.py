import google.generativeai as genai
import os
from dotenv import load_dotenv

# ✅ Load custom .env file for Gemini API Key
load_dotenv(dotenv_path="rqmnts.env")

# ✅ Safely configure the Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# --------------------- TEXT CHUNKING ---------------------
def chunk_text(pdf_text, target_input_tokens=10000, max_output_tokens=8000):
    text_chunks = []
    current_chunk = ""
    current_chunk_tokens = 0
    sentences = pdf_text.split(". ")

    for sentence in sentences:
        sentence_tokens = len(sentence.split())
        if current_chunk_tokens + sentence_tokens <= target_input_tokens:
            current_chunk += sentence + ". "
            current_chunk_tokens += sentence_tokens
        else:
            text_chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "
            current_chunk_tokens = sentence_tokens

    if current_chunk:
        text_chunks.append(current_chunk.strip())

    return text_chunks

# ------------------ SCRIPT GENERATION -------------------
def generate_script_segment(text_chunk, previous_context=""):
    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = f"""
You are a podcast script writer. Generate a lively, casual, and chill podcast script for two speakers, Ryan and Sarah, based on the following text.

Summarize the text while retaining all key information and maintaining continuity with previous segments.

Your goals:
- Keep it conversational and friendly.
- Include 1–2 contextual jokes or witty remarks.
- Avoid using markdown, asterisks, or stage directions like (chuckles).
-Strictly avoid any kinds of asterisks generations.
- while keeping it fun give as much knowledge about the topic as you can.
-even though the input is slightly less try generating huge amount of script while staying on the topic.
- Use real interjections like "Haha!", "Whoa!", or "Oh wow!" to express emotion.
- Start the script with an exciting intro including Ryan and Sarah's names.

❗ Format the output exactly like:
Ryan: [dialogue]
Sarah: [dialogue]

Only use "Ryan:" and "Sarah:" as speaker tags. No other names or prefixes.

Context:
{previous_context}

New Content:
{text_chunk}
    """

    response = model.generate_content(prompt)
    return response.text

# -------------------- FULL SCRIPT ASSEMBLY -------------------
def generate_full_podcast_script(pdf_text):
    text_chunks = chunk_text(pdf_text)
    full_script = ""
    previous_context = ""

    if text_chunks:
        text_chunks[0] = "Welcome to the podcast! " + text_chunks[0]

    for i, chunk in enumerate(text_chunks):
        segment = generate_script_segment(chunk, previous_context)
        full_script += segment + "\n"
        previous_context = chunk

        if i == len(text_chunks) - 1:
            full_script += (
                "Ryan: And that's all for today!\n"
                "Sarah: Thanks for tuning in. Catch you next time!\n"
            )

    # ✅ Save the script to a file
    script_filename = "podcast_script.txt"
    with open(script_filename, "w", encoding="utf-8") as f:
        f.write(full_script)

    print(f"✅ Podcast script saved to: {script_filename}")
    return full_script
