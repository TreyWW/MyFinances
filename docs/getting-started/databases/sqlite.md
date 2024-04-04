# SQLite

Sqlite is a very popular option for local development as it has **no installation**, **is fast for small datasets**, and is
easy to use and backup.

## Configure MyFinances to use sqlite3

By default we use sqlite, but if for some reason you have changed this before you'll need to add this to `.env`

```dotenv title=".env"
DATABASE_TYPE=sqlite
```

Then you'll need to run `python manage.py migrate`

And that's it! Your database will be stored under the file `db.sqlite3`, so keep it safe!
