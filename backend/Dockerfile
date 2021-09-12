FROM python:3.8.5
WORKDIR /code
COPY requirements.txt .
RUN apt-get -y update && apt-get -y upgrade && apt-get -y install nginx && apt-get -y install postgresql && apt-get install -y gunicorn && pip3 install -r ./requirements.txt
COPY . .
ADD entrypoint.sh /entrypoint.sh
RUN chmod a+x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD gunicorn api_foodgram.wsgi:application --bind 0.0.0.0:8000
