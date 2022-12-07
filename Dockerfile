FROM python:3.9-alpine

RUN apk update && apk upgrade && apk add curl bash git

ENV PYENV_ROOT $HOME/.pyenv
ENV DATABASE_URL sqlite:////app/game.db

COPY . $HOME/app
WORKDIR $HOME/app

RUN pip install --upgrade pip && \
  pip install pipenv && \
  pipenv install --deploy --system --ignore-pipfile

CMD gunicorn -b :8080 -w 4 -k uvicorn.workers.UvicornWorker app:asgi_app