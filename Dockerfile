#TAG:v1.0
FROM python:3.9

RUN apt-get upgrade && apt-get update \
    apt-get install \
    software-properties-common -y \
    unzip -y \
    pip install --upgrade pip


RUN pip install -r requirements.txt

WORKDIR /app

COPY . .

EXPOSE 5554

ENTRYPOINT ["/app.py"]