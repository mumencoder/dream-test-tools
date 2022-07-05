
FROM centos:7

RUN yum -y update

RUN yum install -y wget unzip rsync

RUN yum -y install epel-release
RUN yum -y update

RUN yum -y groupinstall "Development Tools"
RUN yum -y install openssl-devel bzip2-devel libffi-devel xz-devel

WORKDIR /tmp/install_python
RUN wget https://www.python.org/ftp/python/3.8.12/Python-3.8.12.tgz && \
    tar xvf Python-3.8.12.tgz

WORKDIR /tmp/install_python/Python-3.8.12

RUN ./configure --enable-optimizations && \
    make altinstall

WORKDIR /

RUN rpm -Uvh https://packages.microsoft.com/config/centos/7/packages-microsoft-prod.rpm && \
    yum -y install dotnet-sdk-6.0

RUN yum -y groupinstall "Compatibility libraries"
RUN yum -y install glibc.i686 libstdc++.i686 libstdc++-devel.i686

RUN yum -y remove git && \
    yum -y remove git-*

RUN yum -y install https://packages.endpointdev.com/rhel/7/os/x86_64/endpoint-repo.x86_64.rpm
RUN yum -y install git

RUN python3.8 -m pip install dominate psutil GitPython

# centos specific
RUN python3.8 -m pip install requests

# install DTT
ADD . /DTT/src
WORKDIR /DTT/src/lib
RUN python3.8 setup.py install
ENV DTT_CONFIG_FILE /DTT/src/box/default-config.py

# run DTT
WORKDIR /DTT/src/scripts