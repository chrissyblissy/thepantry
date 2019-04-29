# The Pantry

A recipebook, inventory and shopping list website. It runs on the Flask-python micro-framework using SQL-Alchemy to run the database and JavaScript, HTML and CSS for the frontend. 

## Getting Started

These instructions will get you a copy of The Pantry that will run on your own webserver.

First thing is to setup Apache to run your webserver. The instructions for installing can be found here - [Apache Install](http://httpd.apache.org/docs/2.4/install.html)

Next is to install MySQL, make sure to install the correct version for your platform - [Install MySQL](https://dev.mysql.com/doc/refman/8.0/en/installing.html)

Next make sure that Python 3 is installed on your system and that you create a [Virtual Environment](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/) before installing the next components

Next install the micro-framework Flask which makes it easier for creating Python files that can serve webpages  - [Install Flask](http://flask.pocoo.org/docs/1.0/installation/)

Next SQLAlchemy needs to be installed so that SQL queries can be run through Python files - [Install SQLAlchemy](https://docs.sqlalchemy.org/en/13/intro.html

Next install Flask-SQLAlchemy so that you can use Flask commands to run SQLAlchemy queries - [Install Flask-SQLAlchemy](https://pypi.org/project/Flask-SQLAlchemy/)

Finally install Werkzeug Security for hashing user passwords - [Install Werkzeug](https://pypi.org/project/Werkzeug/)

## Deployment

### Install and enabling mod_wsgi

WSGI (Web Server Gateway Interface) is an interface between web servers and web apps for python. Mod_wsgi is an Apache HTTP server mod that enables Apache to serve Flask applications - [Deploying mod_wsgi](http://flask.pocoo.org/docs/1.0/deploying/mod_wsgi/)

After you have completed this, make sure to restart your Apache server to apply the changes.

### Initialising the the database

Make sure you are running your virtual environment and then move to the folder 
``` 
cd /thepantry/initialise
```
and then run 
```
export FLASK_APP=’create_database.py’
```
and then start the python3 interpreter
```
python3
```
To create the database you then run the following commands in the python interpreter
```
>>> from create_database import db
>>> db.create_all()
>>> db.session.commit()
```
You should now have a working Flask application and database.

## Built With

* [Flask](http://flask.pocoo.org/) - The web framework used
* [MySQL](https://dev.mysql.com/doc/) - SQL Database
* [SQLAlchemy](https://docs.sqlalchemy.org/en/13/) - Interface between Python and SQL
* [Werkzeug](https://werkzeug.palletsprojects.com/en/0.15.x/utils/) - Security for hashing user passwords

