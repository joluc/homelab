FROM ghcr.io/openclaw/openclaw:2026.7.1

USER root

# Install kubectl (multi-arch)
ARG TARGETARCH
RUN curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/${TARGETARCH}/kubectl" && \
    chmod +x kubectl && \
    mv kubectl /usr/local/bin/kubectl

# Switch back to node user for security
USER node

WORKDIR /app
