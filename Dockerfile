FROM python:3.11-slim

WORKDIR /app
COPY pyproject.toml poetry.lock ./

# configure Poetry
ENV POETRY_VERSION=1.6.1

# installing Poetry
RUN pip install poetry==${POETRY_VERSION} && poetry install --no-root --no-directory
COPY toktik_thumbnailer/ ./toktik_thumbnailer/
RUN poetry install --no-dev

# installing ffmpeg
RUN apt-get update && apt-get install -y ffmpeg

# run the application
CMD ["poetry", "run", "celery", "-A", "toktik_thumbnailer.tasks.app", "worker", "-l", "INFO"]
