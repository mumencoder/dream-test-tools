
DEBIAN_FRONTEND=noninteractive

apt-get update && apt-get upgrade
apt-get install -y wget
wget https://packages.microsoft.com/config/ubuntu/20.04/packages-microsoft-prod.deb -O packages-microsoft-prod.deb && \
    dpkg -i packages-microsoft-prod.deb && \
    rm packages-microsoft-prod.deb
apt-get update && \
    apt-get install -y dotnet-sdk-7.0