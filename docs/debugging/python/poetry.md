# Already installed

The error where `poetry install` says "Skipped for the following reason: Already installed" but `pip freeze` shows that these
clearly aren't installed, you may need to configure your poetry environment to use the local ./venv/ instead of a global one.

First, make sure you aren't in a venv (`deactivate`). If there isn't a /venv/ folder inside of the project, you'll need to
create one with `python -m venv ./venv/`. Now activate it. `./venv/Scripts/activate`.

After you have a venv and it's activated you can run these poetry config commands:

```shell
pip install poetry

poetry config virtualenvs.in-project true

poetry config virtualenvs.path ./venv/

poetry install
```

And this time they should all be correctly installed!

# For other poetry issues, or if this doesn't fix the issue try the following: 
   - Delete all files in your directory associate with poetry.
   - Follow these directions to use the installer on [poetry's website]( https://python-poetry.org/docs/#installing-with-the-official-installer).
