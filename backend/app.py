import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import uuid
from model import style_transfer

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'static/uploads'
RESULT_FOLDER = 'static/results'

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULT_FOLDER'] = RESULT_FOLDER

@app.route('/')
def index():
    return jsonify({
        'message': 'Image Style Transfer API',
        'endpoints': {
            'upload': '/api/upload',
            'get_uploaded_image': '/api/uploads/<filename>',
            'get_result_image': '/api/results/<filename>'
        }
    })

# Add a GET method handler for /api/upload for testing
@app.route('/api/upload', methods=['GET'])
def upload_test():
    return jsonify({
        'message': 'This endpoint requires a POST request with content and style images',
        'required_fields': ['content', 'style']
    })

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'content' not in request.files or 'style' not in request.files:
        return jsonify({'error': 'Missing content or style image'}), 400
    
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
    
    # Save the uploaded files
    content_file.save(content_path)
    style_file.save(style_path)
    
    # Perform style transfer
    try:
        style_transfer(content_path, style_path, result_path)
        
        # Return the URLs for the images
        return jsonify({
            'content': f'/api/uploads/{content_filename}',
            'style': f'/api/uploads/{style_filename}',
            'result': f'/api/results/{result_filename}'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/api/results/<filename>')
def result_file(filename):
    return send_from_directory(app.config['RESULT_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)