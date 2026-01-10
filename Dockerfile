# Use Python 3.11 with Chrome pre-installed
FROM selenium/standalone-chrome:latest

# Switch to root to install packages
USER root

# Install Python and pip
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Set Python path
ENV PYTHONUNBUFFERED=1

# Run the clock worker
CMD ["python3", "railway_clock.py"]
