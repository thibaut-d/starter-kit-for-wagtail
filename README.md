# explore.ac

This is a **work in progress** to create a tool that get structured content from Wikidata as primary source, with secondary sources such as Wikipedias and PubMed. The objective is to display the data in a readable way accoridng to its type. It will also be possible to focus on a certain topic. I.e., if you are a researcher exploring chronic pain related diseases, the list of diseases accessible from the homepage bloc will be narrowed to diseases that have chronic pain as a symptom according to Wikidata metadata.

## Licence

This project is released under the open source MIT licence.

## Technologies used

- Docker + Docker Compose (just "docker-compose up" to get a dev ready environnement)
- Traefik : Not included in this directory. I use it to proxy the different Docker based projects of my remote dev environement. The SSL certificate is provided by Traefik, so that you will have to modify NGINX configuration if you want HTTPS without Traefik.
- NGINX : serve static files and proxy uWSGI
- uWSGI : serve dynamicly generated HTML from Django.
- Python 3 : langage
- Django  : web framework for Python
- Postgres : SQL database
- Redis : cache
- Wagtail : Django based headless CMS that provide a user friendly backend for pages edition
- Boostrap : CSS framework
- PyWikiBot : a python framework to communicate with Wikidata & Wikipedia APIs

## Credits to packages or inspiration sources used for this project

- [BlackrockDigital/startbootstrap-agency](https://github.com/BlackrockDigital/startbootstrap-agency)
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
$ sudo docker-compose run server /bin/bash
```

### Alias

Could help to speed up the process of typing commands...

```bash
alias e="sudo docker-compose exec"
alias ea="sudo docker-compose exec app"
alias m="sudo docker-compose exec app ./manage.py"
alias mmig="sudo docker-compose exec app ./manage.py migrate"
alias mcol="sudo docker-compose exec app ./manage.py collectstatic"
alias mrun="sudo docker-compose exec app ./manage.py runserver 0.0.0.0:8000"
alias msup="sudo docker-compose exec app ./manage.py createsuperuser"
alias es="sudo docker-compose exec server"
```

### Managing Django/Wagtail

```bash
$ sudo docker-compose exec app wagtail start project .  # not needed unless the current site structure is deleted
$ sudo docker-compose exec app pip install -r config/requirements.txt # not needed unless the current site structure is deleted
$ sudo docker-compose exec app ./manage.py migrate # automated in the startup script with fake-initial
$ sudo docker-compose exec app ./manage.py collectstatic # automated in the startup script
$ sudo docker-compose exec app ./manage.py runserver 0.0.0.0:8000 
$ sudo docker-compose exec app ./manage.py createsuperuser
```
@
### Managing uWSGI

Reload uWSGI for the changes to take effect
```bash
$ docker-compose exec app touch /etc/uwsgi/reload-uwsgi.ini
```