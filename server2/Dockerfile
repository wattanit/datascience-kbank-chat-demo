FROM ubuntu:23.10
WORKDIR /root
ENV PACKAGES="\
    python3 \
    python3-pip \
    curl \
    tzdata \
"

ENV PYTHON_PACKAGES="\
    fastapi \
    uvicorn \
    pydantic \
    python-dotenv \
    requests \
    onnxruntime \
    qdrant-client \
    openai \
    openai-whisper \
    numpy \
    pandas \
    websockets \
    tqdm \
    "

# ENV http_proxy http://172.16.222.3:9980/
# ENV https_proxy http://172.16.222.3:9980/
RUN apt-get update \
    && apt-get --no-install-recommends -y install $PACKAGES \
    && pip3 install $PYTHON_PACKAGES --break-system-packages \
    && rm -rf /var/cache/apt/* \
    && rm -rf /var/lib/apt/lists/*

ENV TZ="Asia/Bangkok"
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Copy files into the image
COPY * /root/server/
ENTRYPOINT [ "uvicorn", "server.main:app --reload --port 8000" ]
