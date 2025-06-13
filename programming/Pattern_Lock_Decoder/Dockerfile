# Multi-stage build for security and efficiency
FROM python:3.11-slim-bullseye AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libc6-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Final stage - minimal runtime image
FROM python:3.11-slim-bullseye

# Security: Install security updates
RUN apt-get update && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends \
    dumb-init \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Security: Create non-root user
RUN groupadd -r ctfuser -g 1000 && \
    useradd -r -u 1000 -g ctfuser -s /sbin/nologin -c "CTF user" ctfuser

# Create app directory
WORKDIR /app

# Copy application files
COPY --chown=ctfuser:ctfuser pattern_server_async.py ./

# Security: Set proper permissions
RUN chmod 444 pattern_server_async.py

# Environment variables with secure defaults
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    HOST=0.0.0.0 \
    PORT=9003 \
    FLAG=kctf-jr{advanced_dna_cryptanalyst_2025}

# Security: Drop all capabilities and run as non-root
USER ctfuser

# Use dumb-init to handle signals properly
ENTRYPOINT ["dumb-init", "--"]

# Run the server
CMD ["python", "pattern_server_async.py"]

# Expose port (documentation only, doesn't open ports)
EXPOSE 9003

# Security labels
LABEL security.capabilities.drop="ALL" \
      security.no-new-privileges="true" \
      maintainer="CTF Admin" \
      description="Pattern Lock Decoder CTF Challenge"
