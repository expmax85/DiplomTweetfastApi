FROM python:3.10.0

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y python3-dev supervisor nginx && rm -rf /var/lib/apt/lists/*

WORKDIR /code

COPY supervisord.ini /etc/supervisor/conf.d/supervisord.ini
COPY conf.d/nginx.conf /etc/nginx/nginx.conf
COPY uwsgi.ini /etc/uwsgi/uwsgi.ini

COPY ./requirements.txt /code/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /code

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.ini"]