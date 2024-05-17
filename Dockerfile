# syntax=docker/dockerfile:1.4

FROM --platform=$BUILDPLATFORM python:3.7-alpine AS builder
EXPOSE 8000
WORKDIR /
COPY . /
RUN pip3 install -r requirements.txt --no-cache-dir
RUN python3 manage.py migrate
ENTRYPOINT ["python3"] 
CMD ["manage.py", "runserver", "0.0.0.0:8000"]
