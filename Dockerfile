# Base image
FROM python:3.9

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install dependencies
RUN pip install -r requirements.txt

# Expose port
EXPOSE 5001

# Run application
CMD ["python", "app.py"]
