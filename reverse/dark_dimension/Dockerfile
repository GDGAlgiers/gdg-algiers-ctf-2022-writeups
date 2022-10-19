FROM python:latest

LABEL Maintainer="yalatreche"

COPY speedtest.py ./
COPY dark_dimention.exe ./

RUN chmod +x ./dark_dimention.exe

CMD ["python", "./speedtest.py"]
