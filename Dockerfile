FROM python:3

WORKDIR /rexpaint/


RUN pip install --upgrade pip poetry setuptools wheel

ADD src/ /rexpaint/src/
ADD pyproject.toml poetry.lock /rexpaint/
RUN POETRY_VIRTUALENVS_CREATE=false
RUN poetry install
ENV PYTHONPATH=.
ENTRYPOINT ["poetry", "run", "python", "/rexpaint/src/entrypoint.py"]