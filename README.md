# docker-wagtail

This is a **work in progress** to create a startup environement running under Docker with Wagtail Django based CMS ready for dev.

I will only update this repository when I need to launch a new project. Feel free to reuse with needed updates.

## Technologies used

- Docker + Docker Compose
- Traefik : Not included in this directory. I use it to proxy the different Docker based projects of my remote dev environement. The SSL certificate is provided by Traefik, so that you will have to modify NGINX configuration if you want HTTPS without Traefik.
- NGINX : serve static files and proxy uWSGI
- uWSGI : serve dynamicly generated HTML from Django.
- Python 3 : langage
- Django  : web framework for Python
- Postgres : SQL database
- Redis : cache
- Wagtail : Django based headless CMS that provide a user friendly backend for pages edition

## Other features

- Usable for remote dev
- Rotated db & json backups in Docker volumes
- Backing up your docker volumes can then be done via a local Cron or https://github.com/blacklabelops/volumerize

## Sources

- [erroneousboat/docker-django](https://github.com/erroneousboat/docker-django)
- [testdrivenio/django-on-docker](https://github.com/testdrivenio/django-on-docker)
- [prodrigestivill/docker-postgres-backup-local](https://github.com/prodrigestivill/docker-postgres-backup-local)
- [wagtail/bakerydemo](https://github.com/wagtail/bakerydemo)
- And, of course, the official doc of the different technologies used.

## Setup

### Docker
See installation instructions at: [docker documentation](https://docs.docker.com/install/)

### Docker Compose
Install [docker compose](https://github.com/docker/compose), see installation instructions at [https://docs.docker.com/compose/install/](https://docs.docker.com/compose/install/)

### Environment variables
The file `.env-sample` contains the environment
variables needed in the containers.
It has to be renamed .env, wich is in the .gitignore file of the project.

## Fire it up
Start the container by issuing one of the following commands:
```bash
$ docker-compose up             # run in foreground
$ docker-compose up -d          # run in background
```
## Other commands

### Restart after docker files modification & debug

```bash
$ sudo docker-compose down
$ sudo docker-compose build --no-cache
$ sudo docker-compose --verbose up --force-recreate 
```

### Run commands in container

```bash
# If needed, replace "app" by the name of te service from docker-compose.yml
$ sudo docker-compose run app /bin/bash
$ sudo docker-compose run app python /srv/code/manage.py shell
```

### Alias

This one could help to speed up the process of typing commands.

```bash
alias e="docker-compose exec app"
```

### Managing Django/Wagtail

Enter the container first.

```bash
$ sudo docker-compose run app /bin/bash
$ wagtail start project .  # not needed unless the current site structure is deleted
$ pip install -r requirements.txt # not needed unless the current site structure is deleted
$ ./manage.py migrate # automated in the startup script with fake-initial
$ ./manage.py runserver 0.0.0.0:8000 # automated in the startup script
$ ./manage.py createsuperuser


```
@
### Managing uWSGI

Reload uWSGI for the changes to take effect
```bash
$ docker-compose exec app touch /etc/uwsgi/reload-uwsgi.ini
```