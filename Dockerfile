# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN apt-get update && apt-get install -y libglib2.0-0
RUN pip install --trusted-host pypi.python.org -r requirements.txt
RUN apt-get update && apt-get install -y libgl1-mesa-glx

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV FLASK_APP main

# Run main.py when the container launches
CMD exec gunicorn --bind :$PORT --workers 1 --threads 4 --timeout 600 main:app