Currently we support 2 languages: English and Russian.

## Translate non-translated strings
### Mark string as translatable
To make strings translatable we should use function `gettext_lazy`.
In python code:
```python
from django.utils.translation import gettext_lazy as _

print(_("Hello"))
```

In Django templates you may use `trans` from `i18n` module:
```html
{% load i18n %}
<!DOCTYPE html>
<html>
<body>
    <div>{% trans "Hello" %}
</body>
</html>
```

### Scrape all messages to translate into *.po files
Run following command:
```shell
$ django-admin makemessages --all --ignore=env
```

Execute this command every time you mark new strings for translation or add new strings.

### Translate strings
Open file of the language you want to translate to (e.g. Russian): `locale/ru/LC_MESSAGES/django.po`
Translate every string (value in `msgstr`)
```python
#: frontend/templates/pages/index.html:24
msgid "Dashboard"
msgstr "Обзор"
```

### Compile strings for Django server
Run following command:
```shell
$ django-admin compilemessages --ignore=env
```

This command will generate `*.mo` files in `locale` folder. No need to include it into Git since it's a generated content (ecxcluded via .gitignore).
Execute this command every time you translate strings in `*.po` files.

## Adding new languages
1. Add new language into the `LANGUAGES` variable in `settings.py`:
    ```python
    LANGUAGES = (
        ("en", _("English")),
        ("ru", _("Russian")),
        ("fr", _("French")) # <- e.g. this is a new language
    )
    ```
2. Create new folder for you language
    ```shell
    $ mkdir locale/fr
    ```
3. Collect new strings for your new language
    ```shell
    $ django-admin makemessages --all --ignore=env
    ```
4. Translate strings in `*.po` files
   1. Open in your favourite text editor
   2. Or use GUI tools for translations (e.g. https://poedit.net/)
5. Compile strings into `*.mo` files
   ```shell
   $ django-admin compilemessages --ignore=env
   ```
