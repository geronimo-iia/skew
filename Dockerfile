FROM python:3.8

WORKDIR /opt/skew
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
COPY . .
RUN poetry install

ENTRYPOINT ["python", "-m", "skew"]

