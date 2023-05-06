FROM hdgigante/python-opencv:4.5.5-debian

WORKDIR /app
COPY . .

RUN pip3 install bdist_wheel
RUN pip3 install pyyaap.tar.gz
RUN pip3 install -r requirements.txt

ENTRYPOINT [ "python3", "app.py" ]