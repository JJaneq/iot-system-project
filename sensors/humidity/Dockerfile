FROM python:3.12-slim

WORKDIR /code
COPY requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY sensors/humidity/humidity.py /code/main.py

CMD ["python3", "-u", "main.py"]