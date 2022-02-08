
sudo yum -y update 
sudo yum -y install epel-release
sudo yum -y install https://repo.ius.io/ius-release-el7.rpm 
sudo yum -y update

sudo yum -y groupinstall "Development Tools"
sudo yum -y install openssl-devel bzip2-devel libffi-devel xz-devel
sudo yum -y install wget

sudo yum -y install glibc.i686
sudo yum -y install libstdc++.i686

cd $BASE_DIR 
wget https://www.python.org/ftp/python/3.8.12/Python-3.8.12.tgz
tar xvf Python-3.8.12.tgz
cd Python-3.8*
./configure --enable-optimizations
sudo make altinstall
sudo ln -s /usr/local/bin/python3.8 /bin/python3.8
sudo alternatives --install /bin/python_alt python /usr/bin/python 98
sudo alternatives --install /bin/python_alt python /usr/local/bin/python3.8 99
sudo python3.8 -m pip install --upgrade pip
sudo python3.8 -m pip install GitPython

sudo yum -y remove git
sudo yum -y install git222

sudo rpm -Uvh https://packages.microsoft.com/config/centos/7/packages-microsoft-prod.rpm
sudo yum -y install dotnet-sdk-6.0

cd $BASE_DIR
mkdir dream-storage
cd dream-storage
mkdir source
mkdir config
cd source
git clone https://github.com/mumencoder/dream-test-tools
pushd dream-test-tools/scripts
python3.8 copy_default_config.py
popd
pushd dream-test-tools/lib
sudo python3.8 setup.py develop
popd
git clone https://github.com/mumencoder/Clopendream-parser
