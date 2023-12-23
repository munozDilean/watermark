FROM python:3.9.10-alpine3.14
WORKDIR /srv
# install ffmpeg
RUN apk add ffmpeg
# Install flask for python
RUN pip install --upgrade pip
RUN pip install flask
RUN pip install reportlab
RUN pip install PyPDF2
COPY ./src .
ENV FLASK_APP=app
CMD ["python","app.py"]