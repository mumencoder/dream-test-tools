
DEBIAN_FRONTEND=noninteractive

apt -y install wget unzip rsync
pip install poetry
poetry self update
poetry config virtualenvs.create false