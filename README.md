# yamdb_final
![example workflow](https://github.com/fibboo/yamdb_final/actions/workflows/yamdb_workflow.yaml/badge.svg)

### About:
Cool project with wise API

### Requirements:
docker https://docs.docker.com/engine/install/

### .env template:
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=you_password
DB_HOST=db
DB_PORT=5432
SECRET_KEY='you_secret_key'
```

### Как запустить проект:

Clone project and cd to infra
```
git clone git@github.com:fibboo/infra_sp2.git
cd infra
```
Run with docker-composer
```
docker-composer up -d
```
Migrate, create superuser and collect static
```
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic --no-input
```
Go to check docs http://localhost/redoc/

### If you what to export demo data:
```
docker-compose exec web python manage.py loaddata fixtures.
``` 

