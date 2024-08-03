FROM ubuntu:24.04

LABEL maintainer="Cas van Cooten (@chvancooten)"

WORKDIR /nimplant

# Install system dependencies
RUN apt-get update && apt-get install --no-install-recommends -y \
    build-essential \
    curl \
    git \
    mingw-w64 \
    nim \
    python3 \
    python3-pip \
    rustup \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Rust w/ Cargo opsec improvements
RUN curl https://sh.rustup.rs -sSf | bash -s -- -y --default-toolchain nightly --target x86_64-pc-windows-gnu --profile minimal
ENV PATH="/root/.cargo/bin:${PATH}"
RUN printf "[build]\nrustflags = [\"--remap-path-prefix\", \"/nimplant=/build\", \"-Zlocation-detail=none\"]" > /root/.cargo/config.toml

# Copy files
COPY . /nimplant

# Install Python requirements
RUN pip install --no-cache-dir -r server/requirements.txt --break-system-packages

# Install Nim requirements
RUN cd client; nimble install -d -y; cd ..

# Expose ports
EXPOSE 80
EXPOSE 443
EXPOSE 31337