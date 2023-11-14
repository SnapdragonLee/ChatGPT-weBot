# syntax=docker/dockerfile:1.4
FROM       debian:stable
MAINTAINER yuchuang

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip git

RUN apt-get install -y vim

RUN git clone https://github.com/SnapdragonLee/ChatGPT-weBot.git /opt/ChatGPT-weBot
WORKDIR /opt/ChatGPT-weBot
RUN pip3 install --break-system-packages -r ./requirements.txt

CMD ["/bin/sh", "-c", "python3 main.py"]
