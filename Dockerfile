# syntax=docker/dockerfile:1

FROM python:3

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY read_email.py .

CMD [ "python3", "-u", "./read_email.py" ]