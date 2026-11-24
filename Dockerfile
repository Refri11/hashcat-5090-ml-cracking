FROM nvidia/cuda:12.8.1-devel-ubuntu24.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
        python3 python3-pip \
        git wget ca-certificates p7zip-full \
    && rm -rf /var/lib/apt/lists/*
ARG HASHCAT_VERSION=8.0.0
RUN wget -q https://hashcat.net/files/hashcat-${HASHCAT_VERSION}.7z -O /tmp/hc.7z \
    && 7z x /tmp/hc.7z -o/opt >/dev/null \
    && ln -s /opt/hashcat-${HASHCAT_VERSION}/hashcat.bin /usr/local/bin/hashcat \
    && rm /tmp/hc.7z
RUN pip3 install --no-cache-dir --break-system-packages passlib bcrypt chardet
WORKDIR /work
CMD ["/bin/bash"]
