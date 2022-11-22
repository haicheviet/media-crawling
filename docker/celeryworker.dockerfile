FROM python:3.7

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


#WORKDIR /app/
COPY ./pyproject.toml ./pyproject.toml

# Install dependency
RUN bash -c "if [ $APP_ENV == 'dev' ] ; then poetry install --no-root ; else poetry install --no-root --no-dev ; fi"


WORKDIR /app

COPY ./app /app/app

ENV PYTHONPATH=/app

COPY ./worker-beat-start.sh /worker-beat-start.sh

RUN chmod +x /worker-beat-start.sh

ENTRYPOINT ["bash"]

