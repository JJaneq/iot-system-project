FROM python:3.12-slim

WORKDIR /code
COPY requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY manager/manager.py /code/main.py
COPY manager/db_manager.py /code/db_manager.py

CMD ["python3", "-u", "main.py"]