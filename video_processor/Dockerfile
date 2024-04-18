FROM python:3.8-slim

# Install system libraries required for OpenCV
# Install system libraries required for OpenCV
RUN apt-get update && apt-get install -y \
    libgl1-mesa-dev \
    libglib2.0-0

WORKDIR /usr/src/app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt


EXPOSE 8080
# Run the application

CMD ["python", "processor.py"]