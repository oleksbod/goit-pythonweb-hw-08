# goit-pythonweb-hw-08

## Run PostgreSQL in Docker

```bash
docker run --name db-postgres -p 5432:5432 -e POSTGRES_PASSWORD=05071984 -d postgres

```

Create Db `contacts_app`

## Run migrations

```bash
alembic init -t async migrations

alembic revision --autogenerate -m 'Init'

alembic upgrade head
```

## Run FastAPI

```bash
python main.py
```
