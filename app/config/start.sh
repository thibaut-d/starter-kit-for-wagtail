#!/bin/bash

#####
# Postgres: wait until container is created
#####
until python3 /srv/code/config/database-check.py; do
    sleep 5; echo "*** Waiting for postgres container ..."
done

echo "*** Postgres container is up, launching Django..."

#####
# Django setup
#####
if [ "$PRODUCTION" == "true" ]; then
    # Django: migrate
    #
    # Django will see that the tables for the initial migrations already exist
    # and mark them as applied without running them. (Django won’t check that the
    # table schema match your models, just that the right table names exist).
    echo "==> Django setup, executing: migrate"
    python3 /srv/code/manage.py migrate --fake-initial

    # Django: collectstatic
    #
    # This will upload the files to s3 because of django-storages-redux
    # and the setting:
    # STATICFILES_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
    echo "==> Django setup, executing: collectstatic"
    python3 /srv/code/manage.py collectstatic --noinput -v 3
else
    # Django: reset database
    # https://docs.djangoproject.com/en/1.9/ref/django-admin/#flush
    #
    # This will give some errors when there is no database to be flushed, but
    # you can ignore these messages.
    echo "==> Django setup, executing: flush"
    python3 /srv/code/manage.py flush --noinput
    ## If our app structure will rely on db content, we may not want
    ## to flush the db each time docker is started once dev starts. 
    ## (Un)comment as needed.

    # Django: migrate
    #
    # Django will see that the tables for the initial migrations already exist
    # and mark them as applied without running them. (Django won’t check that the
    # table schema match your models, just that the right table names exist).
    echo "==> Django setup, executing: migrate"
    python3 /srv/code/manage.py migrate --fake-initial

    # Django: collectstatic
    echo "==> Django setup, executing: collectstatic"
    python3 /srv/code/manage.py collectstatic --noinput -v 3

    # start dev server with support for remote dev
    # Edit : this blocks the script because runserver keep the hand. To be studied further...
    # echo "==> Django setup, executing: runserver 0.0.0.0:8000"
    # python3 /srv/code/manage.py runserver 0.0.0.0:8000 
fi

#####
# Launch Cron for Django backups
#####

echo "==> Launching Cron for Django backups"

apt-get install cron -y

# Grant execution rights
chmod +x /srv/code/config/dj_backup_rotated.sh

# Create the log file
echo "Creating log file"
touch /var/log/cron.log

# Add the cron job
echo "Running add to Crontab command"
(crontab -l ; echo "0 3 * * * root /srv/code/config/dj_backup_rotated.sh > /var/log/cron.log 2>&1")| crontab -

crontab -l

echo "Django backups settled"

#####
# Start uWSGI
#####
echo "==> Starting uWSGI ..."
/usr/local/bin/uwsgi --emperor /etc/uwsgi/django-uwsgi.ini







