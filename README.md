# Image Style Transfer Application

This application allows users to apply artistic styles to images using neural style transfer. It consists of a React frontend and a Flask backend with TensorFlow for the style transfer algorithm.

## Project Structure

image-style-transfer-app/
├── backend/ # Flask server and neural style transfer model
│ ├── app.py # Flask application with API endpoints
│ ├── model.py # Neural style transfer implementation
│ ├── requirements.txt # Python dependencies
│ └── static/ # Directories for uploaded and generated images
│ ├── uploads/
│ └── results/
└── frontend/ # React frontend application
├── public/ # Static assets
├── src/ # React components and styles
├── package.json # Node.js dependencies
└── README.md # Frontend documentation

## Backend Setup

1. Navigate to the backend directory:

cd backend

2. Create a virtual environment (recommended):

python -m venv venv
venv\Scripts\activate

3. Install dependencies:

pip install -r requirements.txt

4. Run the server:

python app.py

The server will start on http://localhost:5000.

## Frontend Setup

1. Navigate to the frontend directory:

cd frontend

2. Install dependencies:

npm install

3. Start the development server:

npm start

The React app will open in your browser at http://localhost:3000.

## How to Use

1. Open the React app in your browser
2. Upload a content image (the base image you want to transform)
3. Upload a style image (the image with the artistic style you want to apply)
4. Click "Transfer Style" to process the images
5. Wait for the processing to complete (this may take several minutes)
6. View and download the resulting stylized image

## API Endpoints

- `POST /api/upload`: Upload content and style images for style transfer
- `GET /api/uploads/<filename>`: Retrieve an uploaded image
- `GET /api/results/<filename>`: Retrieve a generated result image

## Technologies Used

- **Frontend**: React, Axios
- **Backend**: Flask, TensorFlow, NumPy, PIL
- **Style Transfer**: VGG19 neural network model
