FROM python:3.12-slim

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt
COPY . /app/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
