
FROM python:3.11-bullseye

COPY ./box /build/box

WORKDIR /build/box/debian

RUN ./update.sh
RUN ./install_dotnet.sh
RUN ./install_git.sh
RUN ./install_byond_dependencies.sh
RUN ./install_DTT_dependencies.sh

COPY . /DTT

RUN ./install_DTT.sh

WORKDIR /DTT