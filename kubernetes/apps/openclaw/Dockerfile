FROM ghcr.io/openclaw/openclaw:2026.2.25

USER root

# Install kubectl
RUN curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" && \
    chmod +x kubectl && \
    mv kubectl /usr/local/bin/kubectl

# Create a symlink for openclaw CLI to make it available in PATH
RUN ln -s /app/openclaw.mjs /usr/local/bin/openclaw && \
    chmod +x /app/openclaw.mjs

# Switch back to node user for security
USER node

WORKDIR /app
