FROM python:3.9

ADD *.py ./

RUN pip install pyzmq

CMD ["python", "-u", "./main.py"]
