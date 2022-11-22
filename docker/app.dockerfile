FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

ARG APP_ENV

ENV APP_ENV "$APP_ENV"

# Config ubuntu
RUN echo "deb http://us.archive.ubuntu.com/ubuntu/ precise main universe" >> /etc/apt/source.list

RUN apt-get update -qq && \
    apt-get update -y

# Install Poetry
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

# Install dependency
COPY ./pyproject.toml ./pyproject.toml
COPY ./prestart.sh ./prestart.sh

RUN bash -c "if [ $APP_ENV == 'dev' ] ; then poetry install --no-root ; else poetry install --no-root --no-dev ; fi"

# Dev jupyter
ARG INSTALL_JUPYTER=false
RUN bash -c "if [ $INSTALL_JUPYTER == 'true' ] ; then pip install jupyterlab ; fi"


COPY ./.env /app/.env
COPY ./app /app/app