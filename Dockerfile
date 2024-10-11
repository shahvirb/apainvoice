# https://github.com/orgs/python-poetry/discussions/1879?sort=top#discussioncomment-216865

# `python-base` sets up all our shared environment variables
FROM python:3.11-slim AS python-base

    # python
ENV PYTHONUNBUFFERED=1 \
    # prevents python creating .pyc files
    PYTHONDONTWRITEBYTECODE=1 \
    \
    # pip
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    \
    # poetry
    # https://python-poetry.org/docs/configuration/#using-environment-variables
    POETRY_VERSION=1.8.3 \
    # make poetry install to this location
    POETRY_HOME="/opt/poetry" \
    # make poetry create the virtual environment in the project's root
    # it gets named `.venv`
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    # do not ask any interactive question
    POETRY_NO_INTERACTION=1 \
    \
    # paths
    # this is where our requirements + virtual environment will live
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"


# prepend poetry and venv to path
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"


# `builder-base` stage is used to build deps + create our virtual environment
FROM python-base AS builder-base
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        # deps for installing poetry
        curl \
        # deps for building python deps
        build-essential

# install poetry - respects $POETRY_VERSION & $POETRY_HOME
RUN curl -sSL https://install.python-poetry.org | python

# copy project requirement files here to ensure they will be cached.
WORKDIR $PYSETUP_PATH
COPY poetry.lock pyproject.toml ./
# Notice that no source code is copied into the container. No need to run poetry install with --no-root because of this

# install runtime deps - uses $POETRY_VIRTUALENVS_IN_PROJECT internally
RUN poetry install --without=dev

# `development` image is used during development / testing
FROM python-base AS development
ENV FASTAPI_ENV=development
# Let's set PYTHONPATH to root dir because the source code folder /apainvoice is located in the root
# and we want python to find that package so that apainvoice scripts can simply be invoked with the -m flag
ENV PYTHONPATH="/:" 

WORKDIR $PYSETUP_PATH

# copy in our built poetry + venv
COPY --from=builder-base $POETRY_HOME $POETRY_HOME
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH

# quicker install AS runtime deps are already installed
RUN poetry install

# Install cron
RUN apt-get update && apt-get install -y cron && apt-get clean
# Add crontab file to the cron directory
COPY crontab /etc/cron.d/crontab
# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/crontab
# Apply cron job
RUN crontab /etc/cron.d/crontab

RUN touch /var/log/update.log

# Copy the entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

WORKDIR /apainvoice

EXPOSE 8000
CMD ["/entrypoint.sh"]

# `production` image used for runtime
# FROM python-base AS production
# ENV FASTAPI_ENV=production
# COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH
# COPY ./apainvoice /apainvoice/
# WORKDIR /apainvoice
# CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "webapp:app"]