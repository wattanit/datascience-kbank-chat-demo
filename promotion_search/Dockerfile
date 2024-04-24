FROM ubuntu:23.10
LABEL MAINTAINER="Zee"
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
    onnxruntime \
    qdrant-client \
    openai \
    openai-whisper \
    python-dotenv \
    pandas \
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
# COPY * /root/
COPY data data
COPY src src
# COPY .env .
ENTRYPOINT [ "python3", "src/service.py" ]

# RUN chmod a+x /root/slack_noti.sh
# ENTRYPOINT ["sh", "/root/run_delta_fund_processor.sh"]
# docker build -f DockerfileDeltaFundProcessor -t mymo-delta-fund-processor:0.0.1 .