from flask import Flask, render_template, request, send_file, jsonify
import os
import time
from werkzeug.utils import secure_filename

# Import custom modules from tayyab folder
from reader import extract_text_from_pdf
from script import generate_full_podcast_script
from example import create_final_podcast  # example.py = TTS file

app = Flask(__name__)

# Configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['PODCAST_FOLDER'] = 'podcasts'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

ALLOWED_EXTENSIONS = {'pdf'}

# Ensure folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PODCAST_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        try:
            # Step 1: Extract text from uploaded PDF
            pdf_text = extract_text_from_pdf(filepath)

            # Step 2: Generate podcast script from text
            script_text = generate_full_podcast_script(pdf_text)

            # Step 3: Convert script to audio podcast
            timestamp = int(time.time())
            output_path = os.path.join(app.config['PODCAST_FOLDER'], f"podcast_{timestamp}.mp3")
            create_final_podcast(script_text, output_path)

            # Optional: Cleanup uploaded file
            os.remove(filepath)

            return jsonify({
                'success': True,
                'message': 'Podcast generated successfully',
                'filename': f"podcast_{timestamp}.mp3"
            })

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/download/<filename>')
def download_file(filename):
    try:
        filepath = os.path.join(app.config['PODCAST_FOLDER'], filename)
        return send_file(filepath, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 404

if __name__ == '__main__':
    app.run(debug=True)
