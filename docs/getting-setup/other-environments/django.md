## Setting up Django

!> Make sure you have followed all of our previous steps in this section before doing this

1. Install our dependencies
   using `python poetry` [click here for installation guide](https://python-poetry.org/docs/#installing-manually)

```bash
poetry install
```

2. Setup your database [(click to view our guide)](getting-setup/databases/)

3. Migrate the database

```shell
python manage.py migrate
```

4. Create an admin account

```bash
python manage.py createsuperuser
```

5. Run the server

```bash
python manage.py runserver
```