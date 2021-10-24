FROM python:2.7-slim
ARG PIPMIRROR=https://pypi.org/simple
COPY requirements.txt .
RUN apt update &&\
    apt install -y --no-install-recommends build-essential python-dev &&\
    pip install --timeout 30 --index $PIPMIRROR --no-cache-dir -r requirements.txt &&\
    rm -rf /var/lib/apt/lists/* requirements.txt
COPY src /SwarmOps
WORKDIR /SwarmOps
EXPOSE 10130
ENTRYPOINT ["bash", "online_gunicorn.sh", "entrypoint"]