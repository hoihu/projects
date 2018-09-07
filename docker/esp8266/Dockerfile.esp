############################################################
# Dockerfile to build ESPOpen toolchain
# Based on Ubuntu 14.04
############################################################

FROM ubuntu:14.04

# Don't ask user options when installing
env DEBIAN_FRONTEND noninteractive
RUN echo APT::Install-Recommends "0"; >> /etc/apt/apt.conf
RUN echo APT::Install-Suggests "0"; >> /etc/apt/apt.conf

# multiverse is required by unrar
RUN apt-get -y update && apt-get install -y \
    git \
    software-properties-common \
    python-software-properties \
    && add-apt-repository -y "deb http://archive.ubuntu.com/ubuntu precise multiverse"
    
RUN apt-get update && apt-get install -y \
    unrar \
    make \
    autoconf \
    automake \
    libtool \
    gcc \
    g++ \
    gperf \
    flex \
    bison \
    texinfo \
    gawk \
    ncurses-dev \
    libexpat-dev \
    python \
    python-serial \
    sed \
    python-dev \
    unzip \
    bash \
    wget \
    nano \
    help2man \
    bzip2

## Clean apt cache
RUN apt-get -y autoremove && \
    apt-get -y clean && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /tmp/* \
    cp /usr/bin/wget wget-o


# create user xtensa - toolchain cannot be built as root...
RUN useradd -ms /bin/bash xtensa
USER xtensa
WORKDIR /home/xtensa

ENV PATH /home/xtensa/esp-open-sdk/xtensa-lx106-elf/bin:$PATH

# GIT checkout and make toolchain
#RUN git clone --recursive https://github.com/pfalcon/esp-open-sdk.git
#WORKDIR /home/xtensa/esp-open-sdk
#RUN make

## Checkout initial uPy image
#WORKDIR /home/xtensa
#RUN git clone --recursive https://github.com/micropython/micropython.git
