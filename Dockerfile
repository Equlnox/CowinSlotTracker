FROM python:3.7-slim-buster
RUN apt-get update && apt-get install -y \
    apt-utils \
    software-properties-common \
    unzip \
    curl \
    xvfb \
    wget \
    gnupg

# install google chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get -y update
RUN apt-get install -y google-chrome-stable

# install chromedriver
RUN apt-get install -yqq unzip
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

# set display port to avoid crash
ENV DISPLAY=:99
COPY ./requirements.txt /vaccine-notifier/requirements.txt
RUN pip install -r /vaccine-notifier/requirements.txt
COPY . /vaccine-notifier/

RUN useradd -ms /bin/bash notifier
RUN chown -R notifier /vaccine-notifier
USER notifier
WORKDIR /vaccine-notifier
CMD ["/usr/local/bin/python", "slot_notifier.py", "Madhya Pradesh", "Jabalpur", "--email-address", "karnalprateek@gmail.com"]