
DEBIAN_FRONTEND=noninteractive

apt remove -y git
add-apt-repository -y ppa:git-core/ppa
apt -y update
apt install -y git