# Using SQLite3 as your local database

Sqlite is a popular option for local development as it has no installation needed, and is fast and compact for small data sources.

## Installation

1. Add these to your django environment variables.

```dotenv
DATABASE_TYPE=postgres
DATABASE_HOST=
DATABASE_PORT=3306
DATABASE_NAME=myfinances# you can choose this, but must first create it (STEP 2)
DATABASE_USER=postgres
DATABASE_PASS=
```

### DATABASE_HOST

This is the main host of your database, for example if ran locally would be "127.0.0.1", if on aws might be `mydb.123456789012.
eu-west-2.rds.amazonaws.com`.

### DATABASE_PORT

This is the port of your host, postgres is likely 5432 though. May be at the end of your DATABASE_HOST, make sure to remove it!

### DATABASE_NAME

This is the name of your database that you created. You will have to do this manually.

- First access your db

```bash
$ psql -h {DATABASE_HOST} -U {DATABASE_USER} -p {DATABASE_PORT} # manually fill out the values in brackets {}
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

> More on environment variables can be through our guides: [env files](getting-setup/other-environments/env-variables) and
[env files for pycharm professional](getting-setup/pycharm/env-variables)

2. Run django migrate command

```bash
python manage.py migrate
```

And that's it - Good luck! Create an issue or discussion if you continue you gain errors, and one of us will help you out :)