
DEBIAN_FRONTEND=noninteractive

apt remove git
add-apt-repository ppa:git-core/ppa
apt update
apt install -y git