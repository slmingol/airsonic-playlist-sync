FROM python:3.11-alpine

# Install dependencies
RUN apk add --no-cache \
    bash \
    tzdata

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY ../requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY ../src/sync_playlist.py .
COPY ../src/discover.py .

# Create directory for config
RUN mkdir -p /config

# Set timezone (can be overridden)
ENV TZ=UTC

# Run as non-root user
RUN addgroup -g 1000 airsonic && \
    adduser -D -u 1000 -G airsonic airsonic && \
    chown -R airsonic:airsonic /app /config

USER airsonic

# Set entrypoint with config path so users only need to pass additional flags
ENTRYPOINT ["python3", "/app/sync_playlist.py", "--config", "/config/config.json"]

# Default arguments - empty so it runs normally, can be overridden with flags like --dry-run
CMD []
