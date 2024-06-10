To setup the project follow our [`Getting Started`](../../getting-started/) guide. It goes through initial install,
configuration setup, and basic usage.

## Test and Lint

Once you have made all the code changes, we require tests to be added. We don't mind if you don't want to add these, that's
completely fine! Just make sure that you put in your PR that tests are still required, so we know.

```bash
### first time setup
pip install poetry # installs poetry
poetry install --no-root --with dev # installs djlint and black
### tests
python manage.py test --parallel # runs our django tests
djlint ./frontend/templates --reformat # runs our djLint formatter for HTML
black ./ # runs our black formatter for python files
mypy . # runs mypy static type check for python files
```

## Pull in your changes

What was that I mentioned? A PR, what's that? A Pull Request is a way of merging your forked code into our shared repo. You
can [create a PR here](https://github.com/TreyWW/MyFinances/pulls), but when you go to
[our repo](https://github.com/TreyWW/MyFinances) you should see a big yellow box saying "would you like to merge *your branch*
into *main*?" and then
press "pull in".

After this, make sure to include as much detail as possible in your PR, especially about tests. We would like 100% test
coverage if possible for any new functions, views, and any other backend code you add.

That's about it! If you struggle at any parts, and just need a bit of support you can either join
our [discord server](https://discord.gg/YDQq2uc2ap) or
create a PR and mention that you need help.

Good luck! Have fun, don't stress if you need to take a break or need help, just speak to us!
