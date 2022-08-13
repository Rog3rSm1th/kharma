FROM python:3.11-rc-slim

ENV POETRY_VERSION=1.1.14
RUN python3 -m pip install poetry==$POETRY_VERSION

WORKDIR /app

COPY poetry.lock pyproject.toml ./
RUN poetry config virtualenvs.in-project true --local
RUN poetry install --no-dev

COPY . .

ENTRYPOINT  ["poetry", "run", "kharma"]