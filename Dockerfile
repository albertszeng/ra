FROM python:3.9-alpine

RUN apk update && apk upgrade && apk add curl bash git

ENV PYENV_ROOT $HOME/.pyenv
ENV DATABASE_URL postgresql://postgres:cWmiSFOpWIAzkDa@ra-db.internal:5432

COPY . $HOME/app
WORKDIR $HOME/app

RUN pip install --upgrade pip && \
  pip install pipenv && \
  pipenv install --deploy --system --ignore-pipfile

# Only one workers to save resources for now.
CMD uvicorn --host 0.0.0.0 --port 8080 --workers 1 --lifespan on --proxy-headers --log-level debug app:asgi_app