# Use Ubuntu base with more build tools pre-installed
FROM python:3.10-bullseye

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Set workdir
WORKDIR /app

# Install system dependencies in one layer
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    pkg-config \
    libx11-dev \
    libatlas-base-dev \
    libgtk-3-dev \
    libboost-python-dev \
    libboost-all-dev \
    libopenblas-dev \
    liblapack-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libgtk-3-dev \
    libatlas-base-dev \
    gfortran \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt /app/

# Try to install with pre-built wheels, fallback to source compilation with limited parallelism
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir --only-binary=:all: dlib==19.24.2 || \
    pip install --no-cache-dir --only-binary=:all: dlib==19.24.1 || \
    pip install --no-cache-dir --only-binary=:all: dlib==19.24.0 || \
    (export MAX_JOBS=1 && pip install --no-cache-dir dlib==19.24.2) || \
    (export MAX_JOBS=1 && pip install --no-cache-dir dlib==19.24.1) || \
    (export MAX_JOBS=1 && pip install --no-cache-dir dlib==19.24.0)

# Install remaining dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . /app

# Create known_faces directory
RUN mkdir -p known_faces

# Expose port
EXPOSE 8000

# Run the app
CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8000"]