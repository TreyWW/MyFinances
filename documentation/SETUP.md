### Index

- [Getting Started](#getting-started)
    - [PyCharm PRO](#pycharm-pro)
    - [No IDE Tools](#no-ide-tools)
    - [Environment Variables](#environment-variables)
        - [PyCharm PRO](#pycharm-pro-1)
    - [Database](#setup-a-local-database)
        - [XAMPP](#xampp-windowslinuxosx)
        - [SQLite](#local-sqlite-database)

# Installation

## Getting Started

1. Fork the project - [Click Here](https://github.com/TreyWW/MyFinances/fork)
   ![image](https://github.com/Strelix/MyFinancesForkTest/assets/73353716/0df56c83-002f-450b-bab9-cf76d8b54d39)
   ![image](https://github.com/Strelix/MyFinancesForkTest/assets/73353716/b13939af-fd94-4cbe-ba77-b8c669cbbfc6)
1. Copy the fork URL
   ![image](https://github.com/Strelix/MyFinancesForkTest/assets/73353716/0a79d0fe-c7af-4c40-9357-4bfc5aa10cc6)
1. Go to a directory that you want the fork to be in
   ![image](https://github.com/Strelix/MyFinancesForkTest/assets/73353716/6ea159d3-a145-4671-968b-b20cf3cd4a03)
1. Go to your terminal
   ![image](https://github.com/Strelix/MyFinancesForkTest/assets/73353716/33ef04ef-e082-441f-95a1-a9d705f7fad7)
   ![image](https://github.com/Strelix/MyFinancesForkTest/assets/73353716/26d72dd7-f9aa-4630-b046-4ff4cb7f4ecb)
   Press enter
1. Now type

```bash
git clone [fork URL copied from earlier] 

# for example:
# git clone https://github.com/YourUsername/MyFinances.git
```

### PyCharm PRO

1. Go into the folder
   ![image](https://github.com/Strelix/MyFinancesForkTest/assets/73353716/e64303bf-e3b7-4b26-ba5a-46c627a4cfaf)
   and press "OK"
1. Now you should have it loaded up in a new tab.
1. Now go to settings (ctrl + alt +s)
   ![image](https://github.com/Strelix/MyFinancesForkTest/assets/73353716/8e7d0bf7-1e1c-4173-9977-0b8b350985af)
1. Now go to your project on the left, and go to "Python Interpreter"
   ![image](https://github.com/Strelix/MyFinancesForkTest/assets/73353716/db1edfd1-e6ed-4ab9-8f62-b991ed0cd968)
1. Now add a local interpreter and select it
   ![image](https://github.com/Strelix/MyFinancesForkTest/assets/73353716/29c0b059-f09e-4f55-a504-4aa14fc53127)
1. Create a local interpreter
   ![image](https://github.com/Strelix/MyFinancesForkTest/assets/73353716/65bb7264-be4f-482f-8385-9aaec547d5b5)

> Before continuing, please install all requirements.txt. Go to requirements.txt, right click, press "Install All Packages"

To refresh the cache, go back to settings, project, and interpreter and install "Django" if not already there
![image](https://github.com/Strelix/MyFinancesForkTest/assets/73353716/5b170100-ccf3-44bf-94c5-7c9fb5104164)

7. Go to "Languages And Frameworks" -> "Django"
   Tick "Enable Django Support"
   Make sure Settings, Project Root and Manage script are all set to the correct values

![image](https://github.com/Strelix/MyFinancesForkTest/assets/73353716/8d73fdc7-0fba-4ab2-8901-1beca6ed39d4)

8. Now you need to add django to your runners. Go to "current file" at the top, and press edit configurations
   ![image](https://github.com/Strelix/MyFinancesForkTest/assets/73353716/88c651c7-37c5-4647-aadf-76adaf6403f5)
   ![image](https://github.com/Strelix/MyFinancesForkTest/assets/73353716/492119f1-b749-4496-890a-cd12012d88be)

### No IDE Tools

1. Setup your [environment variables](#environment-variables)
2. Start the server

```bash
python manage.py runserver
```

## Environment Variables

### PyCharm PRO

1. Go to ".env.sample"
2. Press CTRL+A to select all, and CTRL+C to copy them
   ![image](https://github.com/Strelix/MyFinancesForkTest/assets/73353716/60bded74-b59d-4355-a9b4-111943c5a9d0)

3. Now go to your environment variables section in Run Configuration
   ![image](https://github.com/Strelix/MyFinancesForkTest/assets/73353716/92c85014-b115-448e-bbef-e2f726f9f7dd)
   ![image](https://github.com/Strelix/MyFinancesForkTest/assets/73353716/7dee52df-fe0f-4325-aed0-cff661bfb6b8)
   Then press APPLY and Run!

### Any IDE/None

1. Copy (or move) .env.sample to .env

```bash
cp .env.sample .env
```

## Requirements.txt

```bash
pip install -r requirements.txt
```

or for pycharm, go to requirements.txt, right click -> "Install All Packages"

## Create a user to login with

```bash
python manage.py createsuperuser
```

> Note: Please make sure that the USERNAME is an email, this is the email you login with.

## Setup a local Database

### XAMPP (windows/linux/osX)

1. Install [xampp](https://www.apachefriends.org/)
   ![image](https://github.com/Strelix/MyFinancesForkTest/assets/73353716/4c8119af-3565-4f3d-bddc-a087b26fcf69)
1. Add these [environment variables](#environment-variables)

```dotenv
DATABASE_HOST=127.0.0.1 # leave as 127.0.0.1
DATABASE_NAME=myfinances_development # or the name you gave the database (you will have to create this in localhost/phpmyadmin)
DATABASE_USER=root # leave as root
DATABASE_PASS= # leave blank
```

### Local SQLite Database

Add the [environment variable](#environment-variables)

```dotenv
DATABASE_TYPE=sqlite
```
