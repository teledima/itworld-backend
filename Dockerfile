FROM python:3.12.13-alpine

ENV PYTHONBUFFERED=true

WORKDIR /app

RUN pip install --upgrade pip
RUN pip install poetry~=2.4.0

COPY poetry.lock pyproject.toml README.md /app/
COPY manage.py /app/
COPY src /app/src
COPY tests /app/

RUN poetry config virtualenvs.create false
RUN poetry install

EXPOSE 8000

CMD ["uvicorn", "src.asgi:application", "--host", "0.0.0.0", "--port", "8000"]
