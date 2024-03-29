#!/bin/sh

DEBIAN_FRONTEND=noninteractive

apt-get install -y wget unzip rsync
pip install poetry
poetry self update
poetry config virtualenvs.create false

git clone https://github.com/mumencoder/mumenrepo /src/mumenrepo
cd /src/mumenrepo 
poetry install