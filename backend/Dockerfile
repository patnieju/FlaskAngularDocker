FROM ubuntu:20.04

RUN apt-get update \
    && apt-get install -yq --no-install-recommends \
    build-essential autoconf libtool pkg-config python-dev python3-dev \
    python3 \
    python3-pip \
    libpq-dev

RUN pip3 install --upgrade pip \
    && pip3 install setuptools

# for flask web server
EXPOSE 8081

# set working directory
ADD . /app
WORKDIR /app

# install required libraries
RUN pip3 install -r requirements.txt

# This is the runtime command for the container
CMD python3 mercadona.py
