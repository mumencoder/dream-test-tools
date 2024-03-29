#!/bin/sh

DEBIAN_FRONTEND=noninteractive

apt remove -y git
add-apt-repository -y ppa:git-core/ppa
apt -y update
apt install -y git
git config --global --add safe.directory '*'