FROM python:3.7

WORKDIR /srv/code

# Add current directory to a dir named code in Docker env. It will be the base dir for all further operations.
ADD . /srv/code

RUN apt-get update && apt-get upgrade -y

# Install application requirements
RUN pip install --upgrade pip
RUN pip3 install -r /srv/code/config/requirements.txt

# Add uWSGI config
ADD ./config/django-uwsgi.ini /etc/uwsgi/django-uwsgi.ini

# Create django user, will own the Django app. This is needed
# because we defined this, in the uwsgi.ini file
RUN adduser --no-create-home --disabled-login --group --system django
RUN chown -R django:django /srv/code

# Execute start script to launch uWSGI, Django & Cron backups
CMD ["/srv/code/config/start.sh"]
