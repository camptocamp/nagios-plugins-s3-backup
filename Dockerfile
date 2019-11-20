FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt
RUN mkdir ~/.aws


COPY check_deprecated_backups.py .

CMD [ "python", "./check_deprecated_backups.py", "--exporter", "-p", "default", "-b", "bgdi-backup", "-F", "rancher-server.bgdi.ch"  ]
EXPOSE 8080