# Use an image that already has dlib pre-installed
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set workdir
WORKDIR /app

# Install system dependencies for OpenCV
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgtk-3-0 \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt /app/

# Install dependencies from PyPI (using wheels when available)
RUN pip install --upgrade pip && \
    pip install --no-cache-dir \
    fastapi==0.115.12 \
    uvicorn==0.34.2 \
    opencv-python-headless==4.8.1.78 \
    numpy==1.24.3 \
    python-multipart==0.0.20 \
    pillow==10.0.1 \
    pydantic==2.11.4 && \
    pip install --no-cache-dir \
    https://pypi.org/packages/source/d/dlib/dlib-19.24.0.tar.gz#sha256=734ece0a1c78540b30c0a2ece05e3d9a5f7c8db3a2c5c98c6dd4c96b7a6c1c1e || \
    pip install --no-cache-dir dlib==19.24.0 || \
    pip install --no-cache-dir face-recognition==1.3.0 face_recognition_models==0.3.0

# Copy project files
COPY . /app

# Create known_faces directory
RUN mkdir -p known_faces

# Expose port
EXPOSE 8000

# Run the app
CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8000"]