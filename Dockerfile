FROM pypy:3.9-slim

RUN apt-get update -y && apt-get upgrade -y && apt-get -y install curl bash git postgresql

ENV PYENV_ROOT $HOME/.pyenv
ENV DATABASE_URL postgresql://postgres:cWmiSFOpWIAzkDa@ra-db.internal:5432
ENV DEBUG false

COPY . $HOME/app
WORKDIR $HOME/app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Only one workers to save resources for now.
CMD uvicorn --host 0.0.0.0 --port 8080 --workers 1 --lifespan on --proxy-headers app:asgi_app