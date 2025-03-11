import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import uuid
from model import style_transfer
import threading
import json

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'static/uploads'
RESULT_FOLDER = 'static/results'
PROGRESS_FILE = 'static/progress.json'

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULT_FOLDER'] = RESULT_FOLDER

# Function to get progress from file
def get_progress_value():
    try:
        if os.path.exists(PROGRESS_FILE):
            with open(PROGRESS_FILE, 'r') as f:
                data = json.load(f)
                return data.get('progress', 0)
        return 0
    except Exception as e:
        print(f"Error reading progress: {str(e)}")
        return 0

# Function to set progress to file
def set_progress_value(value):
    try:
        with open(PROGRESS_FILE, 'w') as f:
            json.dump({'progress': value}, f)
        print(f"Progress saved to file: {value}%")
    except Exception as e:
        print(f"Error saving progress: {str(e)}")

@app.route('/api/progress')
def get_progress():
    progress = get_progress_value()
    print(f"Progress requested: Current value is {progress}%")
    return jsonify({'progress': progress})

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'content' not in request.files or 'style' not in request.files:
        return jsonify({'error': 'Missing content or style image'}), 400
    
    # Reset progress at the start
    set_progress_value(0)
    
    content_file = request.files['content']
    style_file = request.files['style']
    
    if content_file.filename == '' or style_file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Generate unique filenames
    content_filename = str(uuid.uuid4()) + os.path.splitext(content_file.filename)[1]
    style_filename = str(uuid.uuid4()) + os.path.splitext(style_file.filename)[1]
    result_filename = str(uuid.uuid4()) + '.jpg'
    
    content_path = os.path.join(app.config['UPLOAD_FOLDER'], content_filename)
    style_path = os.path.join(app.config['UPLOAD_FOLDER'], style_filename)
    result_path = os.path.join(app.config['RESULT_FOLDER'], result_filename)
    
    try:
        # Save the uploaded files
        content_file.save(content_path)
        style_file.save(style_path)
        
        # Log successful file save
        print(f"Files saved successfully: {content_path}, {style_path}")
        
        # Simple function to update progress
        def update_progress(value):
            set_progress_value(value)
            print(f"Progress updated to {value}%")
        
        # Start style transfer in a separate thread
        def process_style_transfer():
            try:
                print("Starting style transfer in background thread...")
                style_transfer(content_path, style_path, result_path, update_progress)
                print(f"Style transfer completed: {result_path}")
            except Exception as e:
                import traceback
                print(f"Style transfer error: {str(e)}")
                print(traceback.format_exc())
        
        # Start the processing thread
        processing_thread = threading.Thread(target=process_style_transfer)
        processing_thread.daemon = True
        processing_thread.start()
        
        # Return the URLs for the images immediately
        return jsonify({
            'content': f'/api/uploads/{content_filename}',
            'style': f'/api/uploads/{style_filename}',
            'result': f'/api/results/{result_filename}'
        })
    except Exception as e:
        import traceback
        print(f"File handling error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': f'File handling failed: {str(e)}'}), 500

@app.route('/api/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/api/results/<filename>')
def result_file(filename):
    # Check if the file exists before serving it
    file_path = os.path.join(app.config['RESULT_FOLDER'], filename)
    if os.path.exists(file_path):
        return send_from_directory(app.config['RESULT_FOLDER'], filename)
    else:
        return jsonify({'error': 'Result file not found'}), 404

if __name__ == '__main__':
    # Disable auto-reloading to prevent issues with TensorFlow
    app.run(debug=True, use_reloader=False)