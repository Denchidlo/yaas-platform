FROM hdgigante/python-opencv:4.6.0-ubuntu

## install dependencies
RUN apt-get update \
    && apt-get -y install libpq-dev gcc 
    
RUN apt -y update \
    && apt install -y python3-pydub

RUN apt-get -y update && apt-get -y install cron

## set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app
COPY . .

COPY crontab /etc/cron.d/crontab
RUN chmod 0644 /etc/cron.d/crontab
RUN /usr/bin/crontab /etc/cron.d/crontab

# run crond as main process of container


RUN pip3 install -r requirements.txt
RUN pip3 install pyyaap.tar.gz

CMD ["cron", "-f"]