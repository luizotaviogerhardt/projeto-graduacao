FROM ubuntu:16.04
MAINTAINER Luiz Gerhardt <luizgerhardt93@gmail.com>

USER root

RUN apt-get update -qqy
RUN apt-key update
RUN apt-get -qqy --no-install-recommends install \
    python \
    python-pip \
    python3 \
    python3-pip \
&& rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
RUN pip install \
	flask \

COPY . /usr/app

EXPOSE 3000
