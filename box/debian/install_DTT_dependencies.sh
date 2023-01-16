
DEBIAN_FRONTEND=noninteractive

apt-get install -y wget unzip rsync
pip install poetry
poetry self update
poetry config virtualenvs.create false