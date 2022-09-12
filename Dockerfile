FROM python:3.8.8-slim-buster
# Build deps
ENV BUILD_DEPS="wget gcc build-essential"
RUN apt-get update \
    && apt-get install -y --no-install-recommends $BUILD_DEPS


# Project initialization:
WORKDIR /code
COPY poetry.lock pyproject.toml /code/

# Project initialization:
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi

# Creating folders, and files for a project:
COPY . /code


EXPOSE 8000
CMD ["python3", "manage.py", "runserver"]
