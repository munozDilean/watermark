FROM python:3.9.18-slim
WORKDIR /srv
# install ffmpeg
RUN apt update
RUN apt -y install ffmpeg

COPY ./requirements.txt ./
# Install flask for python
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src ./src
WORKDIR /srv/src

ENV FLASK_APP=app
CMD ["python","app.py"]