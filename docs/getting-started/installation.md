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

1. Install our dependencies using [python poetry](https://python-poetry.org/docs/#installing-manually)
   ```shell
   pip install poetry
   poetry install --no-root
   ```
2. Setup a database (we suggest using sqlite so there's no installation!)
3. Compile translations
    ```shell
    django-admin compilemessages --ignore=env
    ```
4. Migrate the database
    ```shell
    python manage.py migrate
    ```
5. Create an administrator account
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

### Webpack for JS

Webpack is used to bundle our javascript into one file to make development easier and speed up builds.

1. Run webpack dev

```shell
npm run webpack-dev
```
