FROM python:3.7-slim-buster
RUN apt-get update && apt-get install -y \
    software-properties-common \
    unzip \
    curl \
    xvfb \
    wget

RUN printf 'deb http://deb.debian.org/debian/ unstable main contrib non-free' >> /etc/apt/sources.list.d/debian.list
RUN apt-get update
RUN apt-get install -y --no-install-recommends firefox
# Gecko Driver
ENV GECKODRIVER_VERSION 0.23.0
RUN wget --no-verbose -O /tmp/geckodriver.tar.gz https://github.com/mozilla/geckodriver/releases/download/v$GECKODRIVER_VERSION/geckodriver-v$GECKODRIVER_VERSION-linux64.tar.gz \
  && rm -rf /opt/geckodriver \
  && tar -C /opt -zxf /tmp/geckodriver.tar.gz \
  && rm /tmp/geckodriver.tar.gz \
  && mv /opt/geckodriver /opt/geckodriver-$GECKODRIVER_VERSION \
  && chmod 755 /opt/geckodriver-$GECKODRIVER_VERSION \
  && ln -fs /opt/geckodriver-$GECKODRIVER_VERSION /usr/bin/geckodriver \
  && ln -fs /opt/geckodriver-$GECKODRIVER_VERSION /usr/bin/wires

COPY . /vaccine-notifier/
RUN pip install -r /vaccine-notifier/requirements.txt

RUN useradd -ms /bin/bash notifier
RUN chown -R notifier /vaccine-notifier
USER notifier
WORKDIR /vaccine-notifier
CMD ["/usr/local/bin/python", "slot_notifier.py", "Madhya Pradesh", "Jabalpur", "--email-address", "karnalprateek@gmail.com"]