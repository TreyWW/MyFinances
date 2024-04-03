# Postgres

Postgres is a popular database type as it allows you to scale easily. We suggest postgres for production rather than local
development, but you can use it for either :)

## Using Postgres as your local database

1. Add these to your django environment variables.

```dotenv title=".env"
DATABASE_TYPE=postgres
DATABASE_HOST=
DATABASE_PORT=5432
DATABASE_NAME=myfinances# you can choose this, but must first create it (STEP 2)
DATABASE_USER=postgres
DATABASE_PASS=
```

### DATABASE_HOST

This is the main host of your database, for example if ran locally would be "127.0.0.1",
if on aws might be `mydb.123456789012.eu-west-2.rds.amazonaws.com`.

### DATABASE_PORT

This is the port of your host, postgres is likely 5432 though. May be at the end of your DATABASE_HOST, make sure to remove it!

### DATABASE_NAME

This is the name of your database that you created. You will have to do this manually.

- First access your db

```bash
psql -h {DATABASE_HOST} -U {DATABASE_USER} -p {DATABASE_PORT} # manually fill out the values in brackets {}
```

- Then run this SQL command:

```sql
CREATE DATABASE myfinances # you can call "myfinances" whatever you like
```

- Use this "myfinances" or whatever you called it in the `DATABASE_NAME` variable

### DATABASE_USER

This is the user that you use to login to your postgres server with, might be "postgres" or "admin"

### DATABASE_PASS

This is the password that you use to login to your postgres server with

2. Run django migrate command

```bash
python manage.py migrate
```
