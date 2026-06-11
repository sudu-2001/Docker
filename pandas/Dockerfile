# Use an official lightweight Python runtime
FROM python:3.10-slim

# Set working directory inside the container
WORKDIR /app

# Copy requirements from your current folder context and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything else inside the docker/pandas folder into /app
COPY . .

# Expose the internal Flask application port
EXPOSE 5001

# Run the reconciliation application
CMD ["python", "file.py"]
