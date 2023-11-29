FROM python:3.11.6

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt
COPY ./.env /code/.env

RUN python3.11 -m pip install --no-cache-dir -r /code/requirements.txt

COPY ./app /code/app
COPY ./main.py /code/main.py

CMD ["python3.11", "main.py"]