flake8-check:
	flake8 --config=.flake8

black-check:
	black . --config pyproject.toml --check

isort-check:
	isort -c . --diff

black:
	black . --config pyproject.toml

isort:
	isort .

linters-check: isort-check black-check flake8-check

linters: isort black flake8-check

up:
	docker-compose up -d

up-local:
	docker-compose -f docker-compose.yml -f docker-compose.local.yml up -d

build:
	docker-compose up -d --build

build-local:
	docker-compose -f docker-compose.yml -f docker-compose.local.yml up -d --build

docker-pytest-run:
	docker-compose exec app pytest -s -p no:warnings -vv -x tests/

cleanup:
	docker-compose down

mypy:
	mypy ./bigbro/
