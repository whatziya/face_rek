# Face Recognition API Backend

A FastAPI-based backend service for face recognition using OpenCV and face_recognition library. Designed to work with ESP32-CAM clients for automated face detection and identification.

## Features

- **Face Recognition**: Advanced facial recognition using dlib neural networks
- **Face Registration**: Add new faces to the recognition database
- **RESTful API**: Clean HTTP endpoints for all operations
- **CORS Support**: Cross-origin requests enabled
- **Image Processing**: Automatic image format handling and preprocessing
- **Database Management**: File-based known faces storage
- **Confidence Scoring**: Recognition results with confidence percentages
- **Face Location**: Bounding box coordinates for detected faces

## Technology Stack

- **FastAPI**: Modern Python web framework
- **face_recognition**: Advanced facial recognition library
- **OpenCV**: Computer vision and image processing
- **dlib**: Machine learning library for face detection
- **NumPy**: Numerical computing
- **Uvicorn**: ASGI server for production deployment

## Installation

### Local Development

1. **Clone Repository**
```bash
git clone <repository-url>
cd face-recognition-backend
```

2. **Create Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Run Development Server**
```bash
python app.py
# or
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### Production Deployment (Google Cloud)

1. **Prepare VM Instance**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

2. **Install System Dependencies**
```bash
sudo apt install build-essential cmake
sudo apt install libopenblas-dev liblapack-dev
sudo apt install libx11-dev libgtk-3-dev
```

3. **Setup Application**
```bash
git clone <repository-url>
cd face-recognition-backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

4. **Configure Gunicorn Service**
```bash
sudo nano /etc/systemd/system/face-recognition.service
```

5. **Setup Nginx Reverse Proxy**
```bash
sudo apt install nginx
sudo nano /etc/nginx/sites-available/face-recognition
```

## API Endpoints

### Root Endpoint
```http
GET /
```
Returns API status and number of known faces.

**Response:**
```json
{
  "message": "Face Recognition API is running",
  "known_faces": 5
}
```

### Face Recognition
```http
POST /recognize
```
Recognize faces in uploaded image.

**Parameters:**
- `file`: Image file (multipart/form-data)

**Response:**
```json
{
  "faces_found": 2,
  "results": [
    {
      "name": "John Doe",
      "confidence": 0.85,
      "location": {
        "top": 50,
        "right": 150,
        "bottom": 120,
        "left": 80
      }
    }
  ]
}
```

### Face Registration
```http
POST /register
```
Register a new face in the system.

**Parameters:**
- `name`: Person's name (form parameter)
- `file`: Image file (multipart/form-data)

**Response:**
```json
{
  "message": "Face registered successfully for John Doe",
  "file": "john_doe_20231201_143022.jpg"
}
```

### List Known Faces
```http
GET /known_faces
```
Get list of all registered faces.

**Response:**
```json
{
  "known_faces": ["John Doe", "Jane Smith", "Bob Johnson"]
}
```

### Delete Face
```http
DELETE /known_faces/{name}
```
Remove a person from the recognition database.

**Response:**
```json
{
  "message": "Successfully removed all faces for John Doe"
}
```

## File Structure

```
face-recognition-backend/
├── app.py                 # Main FastAPI application
├── requirements.txt       # Python dependencies
├── known_faces/          # Directory for registered face images
│   ├── john_doe_20231201_143022.jpg
│   └── jane_smith_20231201_143055.jpg
├── README.md
└── .gitignore
```

## Configuration

### Environment Variables

```bash
export PORT=8000  # Server port (default: 8000)
```

### Face Recognition Settings

The system automatically optimizes recognition based on image quality and available processing power. Key parameters:

- **Face Detection**: Uses HOG-based detector for speed
- **Face Encoding**: 128-dimensional face encodings
- **Comparison Threshold**: Automatic threshold based on face distances
- **Image Processing**: Automatic RGB conversion and preprocessing

## Usage Examples

### Register a New Face
```bash
curl -X POST "http://localhost:8000/register" \
  -F "name=John Doe" \
  -F "file=@john_photo.jpg"
```

### Recognize Faces
```bash
curl -X POST "http://localhost:8000/recognize" \
  -F "file=@group_photo.jpg"
```

### List All Known Faces
```bash
curl "http://localhost:8000/known_faces"
```

## Error Handling

The API provides comprehensive error handling:

- **400 Bad Request**: Invalid file format or multiple faces in registration
- **404 Not Found**: Face not found for deletion
- **500 Internal Server Error**: Processing errors with detailed messages

### Common Errors

1. **No Face Detected**
```json
{
  "detail": "No face detected in the image"
}
```

2. **Multiple Faces in Registration**
```json
{
  "detail": "Multiple faces detected in the image. Please upload an image with just one face."
}
```

3. **Invalid File Format**
```json
{
  "detail": "File must be an image"
}
```

## Performance Optimization

### Image Processing
- Automatic image resizing for optimal processing speed
- RGB color space conversion for face_recognition library
- Memory-efficient image handling

### Face Recognition
- Efficient face encoding comparison using NumPy
- Batch processing capability for multiple faces
- Optimized distance calculations

## Security Considerations

- **Input Validation**: Strict file type checking
- **File Storage**: Secure local file storage system
- **CORS Policy**: Configurable cross-origin settings
- **Rate Limiting**: Consider implementing for production

## Deployment Notes

### Google Cloud Platform

1. **VM Configuration**: Use compute-optimized instances for better performance
2. **Firewall Rules**: Open HTTP port (80) for external access
3. **SSL Certificate**: Implement HTTPS for production
4. **Auto-scaling**: Consider Cloud Run for automatic scaling

### Docker Deployment

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Troubleshooting

### Installation Issues

1. **dlib Installation Problems**
```bash
sudo apt install build-essential cmake
pip install dlib
```

2. **OpenCV Issues**
```bash
sudo apt install python3-opencv
pip install opencv-python
```

3. **Memory Issues**
- Use swap file for compilation on low-memory systems
- Consider using pre-compiled wheels

### Runtime Issues

1. **Face Recognition Accuracy**
- Ensure good lighting in registration photos
- Use high-quality images for registration
- Register multiple angles of the same person

2. **Performance Issues**
- Reduce image resolution for faster processing
- Use face detection optimizations
- Consider GPU acceleration for high-volume usage
