#!/bin/sh

DEBIAN_FRONTEND=noninteractive

add-apt-repository -y ppa:deadsnakes/ppa
apt -y install python3.11-dev python3.11-venv
