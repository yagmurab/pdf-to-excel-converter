# Base image
FROM python:3.9-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-tur \
    && apt-get clean

# Install Python packages
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the app files
COPY . /app

# Set working directory
WORKDIR /app

# Expose Streamlit port
EXPOSE 8501

# Run the app
CMD ["streamlit", "run", "app.py"]
