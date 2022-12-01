
FROM python:3.10.8-bullseye

COPY . /build

RUN /build/box/debian/install_dotnet.sh 

RUN apt-get install -y wget unzip rsync
RUN apt-get install -y gcc-multilib lib32stdc++6
#RUN pip install pipx
#RUN pipx install poetry && pipx ensurepath && poetry self update
#RUN poetry config virtualenvs.create false