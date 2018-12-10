FROM ubuntu:16.04
MAINTAINER Luiz Gerhardt <luizgerhardt93@gmail.com>

USER root

RUN apt-get update -qqy
RUN apt-key update
RUN apt-get -qqy --no-install-recommends install \
    libc6-dev \
    gcc \
    python \
    python-pip \
    python3 \
    python3-pip \
&& rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
RUN pip install flask
RUN pip install flask-cors


RUN mkdir /app
COPY ./app /app

WORKDIR /app
EXPOSE 5000
ENTRYPOINT ["python"]
CMD ["main.py"]
