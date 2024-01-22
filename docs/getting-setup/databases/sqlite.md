# Using SQLite3 as your local database


Sqlite is a popular option for local development as it has no installation needed, and is fast and compact for small data sources.

## Installation

1. Add `DATABASE_TYPE=sqlite` in your django environment variables. More on environment variables can be found [here](getting-setup/other-environments/env-variables)
2. Run django migrate command 
```bash
python manage.py migrate 
```

And that's it! Now you'll have a database called `db.sqlite3` in your root directory. You can connect to it with the required 
sqlite drivers manually - but django will do this for you!