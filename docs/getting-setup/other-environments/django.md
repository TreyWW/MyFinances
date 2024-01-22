## Setting up Django

!> Make sure you have followed all of our previous steps in this section before doing this

1. Install our dependencies using `pip`

```bash
pip install -r requirements.txt
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