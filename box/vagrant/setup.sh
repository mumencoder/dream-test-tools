
declare -A osInfo;
osInfo[/etc/centos-release]=yum
osInfo[/etc/os-release]=apt

declare packMan;

for f in ${!osInfo[@]}
do
    if [[ -f $f ]];then
        echo Package manager: ${osInfo[$f]}
	    packMan=${osInfo[$f]}
	    break
    fi
done

if [[ $packMan == "yum" ]];then
	sudo $packMan -y update 
	sudo $packMan -y install epel-release
	sudo $packMan -y install https://repo.ius.io/ius-release-el7.rpm 
fi

sudo $packMan -y update

if [[ $packMan == "yum" ]];then
	sudo $packMan -y groupinstall "Development Tools"
	sudo $packMan -y install openssl-devel bzip2-devel libffi-devel xz-devel
	sudo $packMan -y install wget
else
	sudo $packMan -y install gcc
	sudo $packMan -y install libc6
	sudo $packMan -y install libstdc++6
	sudo $packMan -y install libssl-dev llvm libncurses5-dev libncursesw5-dev tk-dev python-openssl
fi


cd $BASE_DIR 
wget https://www.python.org/ftp/python/3.8.12/Python-3.8.12.tgz
tar xf Python-3.8.12.tgz
cd Python-3.8.12/
if [[ $packMan == "yum" ]];then
	./configure --enable-optimizations
		
fi
sudo make altinstall
sudo ln -s /usr/local/bin/python3.8 /bin/python3.8
sudo python3.8 -m pip install --upgrade pip
sudo python3.8 -m pip install GitPython

if [[ $packMan == "yum" ]];then
	sudo $packMan -y remove git
	sudo $packMan -y install git222
	sudo rpm -Uvh https://packages.microsoft.com/config/centos/7/packages-microsoft-prod.rpm
	sudo $packMan -y install dotnet-sdk-6.0
else
	sudo $packMan -y install dotnet-runtime-6.0
fi

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
