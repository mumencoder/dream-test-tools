
FROM ubuntu:20.04

# update base box
RUN apt clean && apt -y update 

# basic tools
RUN apt install -y wget unzip rsync tini

# setup repos
RUN apt install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa
RUN wget https://packages.microsoft.com/config/ubuntu/20.04/packages-microsoft-prod.deb -O packages-microsoft-prod.deb && \
    dpkg -i packages-microsoft-prod.deb && \
    rm packages-microsoft-prod.deb

# update
RUN apt -y update

# setup python
RUN apt install -y python3-pip
RUN python3 -m pip install setuptools

# setup dotnet
RUN apt-get install -y apt-transport-https && \
    apt-get update && \
    apt-get install -y dotnet-sdk-6.0

# byond dependencies
RUN apt install -y gcc-multilib lib32stdc++6

# tools for DTT
RUN add-apt-repository ppa:git-core/ppa && \
    apt install -y git
RUN python3 -m pip install dominate psutil GitPython

# install DTT
ADD . /DTT/src
WORKDIR /DTT/src/lib
RUN python3 setup.py install
ENV DTT_CONFIG_FILE /DTT/src/box/default-config.py

# run DTT
WORKDIR /DTT/src/scripts

ENTRYPOINT ["/usr/bin/tini", "--"]