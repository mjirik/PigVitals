# Base image
FROM python:3.8-slim

WORKDIR /usr/src/app_requirements

# Copy the current directory contents into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Set the working directory in the container
WORKDIR /usr/src/app

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV FLASK_ENV=production

# Run app.py when the container launches
CMD ["python", "app.py"]
