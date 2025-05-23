# Use official Python image with your version
FROM python:3.10.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set workdir
WORKDIR /app

# Install system dependencies for OpenCV and dlib
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk-3-dev \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libglib2.0-0 \
    libgtk-3-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt /app/

# Install Python dependencies with pre-compiled wheels
RUN pip install --upgrade pip && \
    pip install --no-cache-dir \
    --find-links https://pypi.org/simple/ \
    --prefer-binary \
    dlib==19.24.6 && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . /app

# Create known_faces directory
RUN mkdir -p known_faces

# Expose port (Render uses this)
EXPOSE 8000

# Run the app
CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8000"]