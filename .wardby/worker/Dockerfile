# Coding-worker image for wardby agents working on this repository: wardby's
# published driver plus the Python toolchain this project tests with, so an
# agent can run the full suite -- including the Flask web tests -- inside its
# sandbox, which has no pip and no network at run time.
#
# Build for linux/amd64, push, and pin the resulting digest as the agent's
# codingProfile.workerImageRef (requires the agents:admin scope).
# Driver: https://github.com/wardby/wardby/releases/tag/driver-v3
FROM ghcr.io/wardby/wardby/wardby-coding-worker-driver@sha256:17095388e1c92de60b2cf5669b5846d7976e2b399fd8f667d6131e02ec13db54 AS runtime
RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 python3-pip \
    && python3 -m pip install --no-cache-dir --break-system-packages \
        "pytest>=9.0.3,<10" "ruff>=0.11,<1" "flask>=3.1,<4" \
    && apt-get purge -y --auto-remove python3-pip \
    && rm -rf /var/lib/apt/lists/* \
    # Projects (and this one's CI) say `python`, not `python3`.
    && ln -s /usr/bin/python3 /usr/bin/python
# The sandbox must not contain these; pip is removed so nothing is installed at run time.
RUN test ! -e /usr/bin/docker \
    && test ! -e /usr/bin/ssh \
    && test ! -e /usr/bin/curl \
    && test ! -e /usr/bin/wget \
    && test ! -e /usr/bin/sudo \
    && test ! -e /usr/bin/gcc \
    && test ! -e /usr/bin/make \
    && test ! -e /usr/bin/pip \
    && test ! -e /usr/bin/pip3 \
    && python -m pytest --version \
    && python -m ruff --version \
    && python -c "import flask; print('flask', flask.__version__)"
USER 10001:10001
ENV NODE_ENV=production HOME=/home/wardby
WORKDIR /workspace
ENTRYPOINT ["node", "/opt/wardby/coding-worker/main.js"]
