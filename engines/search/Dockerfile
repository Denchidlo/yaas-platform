FROM hdgigante/python-opencv:4.6.0-ubuntu

## install dependencies
RUN apt-get update \
    && apt-get -y install libpq-dev gcc 
    
RUN apt -y update \
    && apt install -y python3-pydub


## set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app
COPY . .

RUN pip3 install -r requirements.txt
RUN pip3 install pyyaap.tar.gz

ENTRYPOINT ["python3", "app.py"]