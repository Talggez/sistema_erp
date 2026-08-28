FROM python:3.13-slim

WORKDIR /code

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src /code/app
ENV PYTHONPATH=/code/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000", "--reload"]
