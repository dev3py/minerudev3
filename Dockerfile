# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install venv for creating a virtual environment
RUN python -m venv /opt/venv

# Activate the virtual environment
ENV PATH="/opt/venv/bin:$PATH"

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
RUN  pip install python-multipart
RUN sudo apt install libgl1-mesa-dev

# Install detectron2 precompiled wheel
RUN pip install detectron2 --extra-index-url https://wheels.myhloli.com

# Install magic-pdf full-feature package
RUN pip install magic-pdf[full]==0.6.2b1

# Copy the models directory to /tmp
COPY PDF-Extract-Kit/models /tmp/models

# Copy and configure the magic-pdf configuration file
RUN cp magic-pdf.template.json /root/magic-pdf.json

# Ensure the models-dir is set correctly in the configuration file
RUN sed -i 's|"models-dir": ".*"|"models-dir": "/tmp/models"|' /root/magic-pdf.json

# Install FastAPI and Uvicorn
RUN pip install fastapi uvicorn

# Expose port 8000 for the FastAPI app
EXPOSE 8000

# Command to run the FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
