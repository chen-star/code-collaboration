To turn in homework 6, create files (and subdirectories if needed) in
this directory, add and commit those files to your cloned repository,
and push your commit to your bare repository on GitHub.

Add any general notes or instructions for the TAs to this README file.
The TAs will read this file before evaluating your work.

----
URL: http://django-env.sgwhhj57ss.us-east-2.elasticbeanstalk.com/
My `settings.py` contains my password for emails, so I did not commit it.
----
## Steps (for future reference)
### Django Config
1. Run `pip freeze > requirements.txt` to add requirements file
2. Run `mkdir .ebextensions` and add a new file `django.config` with content:
```
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: webapps/wsgi.py
```
replace with the project name

### Set AWS environment
1. Run `eb init -p python-3.6 webapps` and select default region
14) us-east-2 : US East (Ohio)
See `Application webapps has been created.`
2. Run `eb create django-env`
See `2018-11-07 22:57:55    INFO    Successfully launched environment: django-env`
3. Run `eb status` to check for domain name
See `CNAME: django-env.sgwhhj57ss.us-east-2.elasticbeanstalk.com`
Edit `settings.py` file with the `ALLOWED_HOST`
Add above and '127.0.0.1'
4. Deploy again. Run `eb deploy` and `eb open` to check if it is working (without static files)
5. Manage static files
Add
```python
STATIC_URL = '/static/'
STATIC_ROOT = 'static'
```
 to settings and run `python3 manage.py collectstatic`

### Change database
1. Config `postgresql`
a) Connect to `postgresql`
`postgres -D /usr/local/var/postgres`
show `LOG:  database system is ready to accept connections`
(Optional) In a new window, create new user with no password `createuser -P postgres`

b) In a new window, create a new db for `Grumblr`
`createdb -U postgres grumblr`
enter the database `psql -U postgres grumblr`
grant all privileges
`GRANT ALL PRIVILEGES ON DATABASE grumblr TO postgres;`
`\dt` to show all tables
`Ctrl + D` to quit
2. Change to `postgresql` following this link[https://gist.github.com/sirodoht/f598d14e9644e2d3909629a41e3522ad]
a) Dump existing data:
```python
python3 manage.py dumpdata > datadump.json
```
b) Change `settings.py` to Postgres backend.
```python
  DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'grumblr',                      # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': 'postgres',
        'PASSWORD': '',
        'HOST': 'localhost',    # Empty for localhost through domain sockets or           '127.0.0.1' for localhost through TCP.
        'PORT': '',             # Set to empty string for default.
    }

#    'default': {
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#    }
}```
c) Make sure you can connect on PostgreSQL. Then:
```python
python3 manage.py migrate --run-syncdb
```
d) Run this on Django shell to exclude contentype data
```python
python3 manage.py shell
>>> from django.contrib.contenttypes.models import ContentType
>>> ContentType.objects.all().delete()
>>> quit()
```
e) Finally:
```python
python3 manage.py loaddata datadump.json
```
3. Deploy & update
Referencing this page [https://realpython.com/deploying-a-django-app-and-postgresql-to-aws-elastic-beanstalk/#configuring-a-database]
After deployment will get a 500 error: `OperationalError at /
could not connect to server: Connection refused
	Is the server running on host "localhost" (127.0.0.1) and accepting
	TCP/IP connections on port 5432?`
(for my reference only)
username: weitongz
pw: postgrespassword
Modify in `settings`:
```python
if 'RDS_DB_NAME' in os.environ:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': os.environ['RDS_DB_NAME'],
            'USER': os.environ['RDS_USERNAME'],
            'PASSWORD': os.environ['RDS_PASSWORD'],
            'HOST': os.environ['RDS_HOSTNAME'],
            'PORT': os.environ['RDS_PORT'],
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'grumblr',
            'USER': 'postgres',
            'PASSWORD': '',
            'HOST': 'localhost',
            'PORT': '', #5432
        }
    }
```
Still got a programming error.
Add a new file to `.ebextensions`:`02_python.config`
```
container_commands:
  01_migrate:
    command: "python3 manage.py migrate --noinput"
    leader_only: true
```
It can work but with no old data.

### Send actual emails
1) send emails
In `settings.py`, delete `EmailBackend` to use real emails
Use Andrew credentials with
```python
EMAIL_HOST = 'smtp.andrew.cmu.edu'
EMAIL_HOST_USER = <andrewId>
EMAIL_HOST_PASSWORD = <password>
EMAIL_PORT = 587
EMAIL_USE_TLS = True
```
2) make credentials `environ`
`echo NAME=name` and `os.environ.get('EMAIL_HOST_USER')`

3) Set environ to AWS
TA says just not commit the files that contain the credentials...
