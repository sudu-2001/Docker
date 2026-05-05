# Use the latest lightweight Alpine Linux image
FROM alpine:latest

# Install bash and other necessary tools for your script
# Note: --no-cache keeps the image size small by not storing index files
RUN apk add --no-cache bash

# Set the working directory to /didk (as you requested)
WORKDIR /didk

# Copy your local script into the container's /didk folder
# Ensure your script is named 'disk_report.sh' in your local folder
COPY diskspace.sh .

# Grant execute permissions to the script
RUN chmod +x diskspace.sh

# Set the script to run automatically when the container starts
ENTRYPOINT ["/bin/bash", "./diskspace.sh"]
