# pull official base image
FROM python:3.11-slim-buster

# set working directory
WORKDIR /src

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install system dependencies
RUN apt-get update \
  && apt-get -y install netcat gcc postgresql \
  && apt-get clean

# install python dependencies
RUN pip install --upgrade pip
RUN pip install poetry
COPY ./poetry.lock ./pyproject.toml /app/

RUN poetry config virtualenvs.create false
RUN poetry install

# add app
COPY . /src

ENTRYPOINT [ "/entrypoint" ]
