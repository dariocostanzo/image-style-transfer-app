# Image Style Transfer Backend

This is the backend server for the Image Style Transfer application. It uses Flask to serve a REST API and TensorFlow for neural style transfer.

## Setup

1. Create a virtual environment (recommended):
   python -m venv venv
   venv\Scripts\activate

pip install -r requirements.txt

The server will start on http://localhost:5000.

## API Endpoints

- `POST /api/upload`: Upload content and style images for style transfer
- `GET /api/uploads/<filename>`: Retrieve an uploaded image
- `GET /api/results/<filename>`: Retrieve a generated result image

## Directory Structure

- `app.py`: Flask application with API endpoints
- `model.py`: Neural style transfer implementation
- `static/uploads/`: Directory for uploaded images
- `static/results/`: Directory for generated results
