FROM python:3
ENV PYTHONUNBUFFERED=1

RUN apt-get update
RUN apt-get -y install zsh
RUN apt-get -y install celery
RUN apt-get -y install ffmpeg
RUN wget https://github.com/robbyrussell/oh-my-zsh/raw/master/tools/install.sh -O - | zsh || true
RUN export SHELL=/usr/bin/zsh
RUN apt-get install nano

RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt