# ──────────────────────────────────────────────────────────────────────────────
# Wisecow – Dockerfile
# Serves cow wisdom over HTTP (or HTTPS when TLS certs are mounted).
# ──────────────────────────────────────────────────────────────────────────────
FROM ubuntu:22.04

LABEL maintainer="wisecow-devops"
LABEL description="Wisecow: cow wisdom web server"

# Prevent interactive prompts during apt installs
ENV DEBIAN_FRONTEND=noninteractive

# Install runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        fortune-mod \
        fortunes \
        cowsay \
        netcat-openbsd \
        socat \
        bash \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Add cowsay to PATH
ENV PATH="/usr/games:${PATH}"

# Working directory
WORKDIR /app

# Copy application script
COPY wisecow.sh /app/wisecow.sh
RUN chmod +x /app/wisecow.sh

# Port the app listens on
EXPOSE 4499

# TLS certificate mount point (optional – app detects if certs exist)
VOLUME ["/certs"]

# Health-check: verify the port is accepting connections
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD bash -c 'echo -e "GET / HTTP/1.0\r\n" | nc -w 2 localhost 4499 | grep -q "HTTP"' || exit 1

ENTRYPOINT ["/app/wisecow.sh"]
