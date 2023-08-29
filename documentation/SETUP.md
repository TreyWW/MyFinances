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

![img_2.png](img_2.png)
1. Copy the fork URL
![img_7.png](img_7.png)
1. Go to a directory that you want the fork to be in
![img_4.png](img_4.png)
1. Go to your terminal
![img_5.png](img_5.png)
![img_6.png](img_6.png)
Press enter
1. Now type 
```
git clone [fork URL copied from earlier] 

# for example:
# git clone https://github.com/YourUsername/MyFinances.git
```
### PyCharm PRO
1. Go into the folder
![img_8.png](img_8.png)
and press "OK"
1. Now you should have it loaded up in a new tab.
1. Now go to settings (ctrl + alt +s)
![img_9.png](img_9.png)
1. Now go to your project on the left, and go to "Python Interpreter"
![img_10.png](img_10.png)
1. Now add a local interpreter and select it
![img_11.png](img_11.png)
1. Create a local interpreter
![img_12.png](img_12.png)

> Before continuing, please install all requirements.txt. Go to requirements.txt, right click, press "Install All Packages"

To refresh the cache, go back to settings, project, and interpreter and install "Django" if not already there
![img_15.png](img_15.png)

7. Go to "Languages And Frameworks" -> "Django"
Tick "Enable Django Support"
Make sure Settings, Project Root and Manage script are all set to the correct values
> You will also need to come back here later for env variables

![img_13.png](img_13.png)

8. Now you need to add django to your runners. Go to "current file" at the top, and press edit configurations
![img_14.png](img_14.png)
![img_16.png](img_16.png)

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
![img_17.png](img_17.png)
3. Now go to your environment variables section in Run Configuration
![img_14.png](img_14.png)
![img_18.png](img_18.png)
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
Install [xampp](https://www.apachefriends.org/)
![img_19.png](img_19.png)
### Local SQLite Database
Coming Soon