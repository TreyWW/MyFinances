# Installation

## Fork the repo

Go to our github project and press fork ([or visit this url directly](https://github.com/TreyWW/MyFinances/fork)).

- Fill out the `repository name`
- Press `create fork`
- Copy your fork url

## Clone the project

Go to a directory that you want the fork to be in, e.g. `E:/projects/` and go into the terminal

```shell
git clone [copied fork url]

# for example
# git clone https://github.com/YourUserName/MyFinances.git
```

## Setup environment variables

1. Copy the template environment variables
    ```shell
    cp .env.sample .env
    ```
2. Edit the template environment variables to your needs, e.g. with nano
    ```shell
   nano .env
    ```

## Setup the backend (Django)

!!! warning "Make sure you have done the previous steps first!"


1. Create a virtual environment and activate it

	```shell
	python -m venv ./venv/

 	./venv/Scripts/activate
	```

2. Install our dependencies using [python poetry](https://python-poetry.org/docs/#installing-manually)
   ```shell
   pip install poetry

   poetry install --no-root --with mypy,django,dev
   ```
3. Setup a database (we suggest using sqlite so there's no installation!)
   To do this you can use one of our database guides, we currently only support 3 databases:
   	- [SQlite3 (recommended for dev)](./databases/sqlite.md)
   	- [Postgres3 (recommended for prod)](./databases/postgres.md)
   	- [Mysql](./databases/mysql.md)

4. Migrate the database
    ```shell
    python manage.py migrate
    ```
5.  Create an administrator account
    ```shell
    python manage.py createsuperuser
    ```

6. Run the application
    ```shell
    python manage.py runserver
    ```

## Setup the frontend

!!! warning "Please NEVER edit the output.css file to make custom css changes, only manually edit the input.css file."

### Tailwind CSS

1. Install NPM (follow a guide like [this](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm))
   2. Run npm install
       ```shell
       npm install
       ```

#### Tailwind Watch

You can run tailwind watch to update the CSS files as you use tailwind classes. This will auto-build every time you make
changes, providing you still have the terminal open.

```shell
npm run tailwind-watch
```

!!! note "Keep in mind, if you don't run tailwind watch you WILL NOT be able to use tailwind classes and may break new changes."

#### Tailwind Build

To be honest, tailwind watch is nice, but especially on my windows PC it is VERY CPU and Memory intesive, every single change,
even 1 character causes a re-watch, and this is a lot... Instead of that, you can use `tailwind-build` to only do a one-time
build. You need to remember to run the command after a major update though, incase you add new classes.

```shell
npm run tailwind-build
```

### Webpack for JS

Webpack is used to bundle our javascript into one file to make development easier and speed up builds. The project now uses
chunks to load javascript, so you should see a few files with ids such as `937`. Django will automatically pick these up.


#### Run webpack dev

```shell
npm run webpack-dev # this only runs it once

npm run webpack-watch # this does the same as above, but listens for updates
```
