#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Notes for the translation process using Flask-Babel
-once characters for translations were identified (enclosed with gettext or _())
-then run the following in terminal; this creates the translation template "messages.pot"
    venv/bin/pybabel extract -F babel.cfg -o messages.pot app
    or this below to include the lazy_gettext wrapper; delayed translation
    venv/bin/pybabel extract -F babel.cfg -k lazy_gettext -o messages.pot app
-then run this below to create the translations file specific to the language specified
-es or spanish for this example
    venv/bin/pybabel init -i messages.pot -d app/translations -l es
when you want to update just run the following
    venv/bin/pybabel extract -F babel.cfg -o messages.pot app
    venv/bin/pybabel update -i messages.pot -d app/translations
once you have the messages.po file found in the translations folder
you can now select a translation app to give you the translations
for each specific lines identified by Babel; Sample: Poedit though not free
it will just update the same the .po file which you can then use
to compile and produces .mo file that will be used for the actual translation
    venv/bin/pybabel compile -d app/translations
if it doesnt compile and returns fuzzy flag then use this below
    venv/bin/pybabel compile -d app/translations
"""

import os
import ConfigParser
import json

# get directories
basedir = os.path.dirname(os.path.abspath(__file__))
config_dir = "{}/etc/credentials".format(basedir)
appsecret_dir = "{}/etc/appsecret".format(basedir)
file_dir = [config_dir, appsecret_dir]

if os.environ.get('HEROKU') is None:
    # store configurations
    config = {}
    for file in file_dir:
        config_file = open(file, "r")
        config_parser = ConfigParser.ConfigParser()
        config_parser.readfp(config_file)
        for section in config_parser.sections():
            for k, v in config_parser.items(section):
                if k not in config:
                    config[k] = v

# for row in config:
#     print str(config) + " : " + str(config[row])

WTF_CSRF_ENABLED = True

PROVIDERS = [
    {'name': 'Google', 'url': 'https://www.google.com/accounts/o8/id'},
    {'name': 'Yahoo', 'url': 'https://me.yahoo.com'},
    {'name': 'AOL', 'url': 'http://openid.aol.com/<username>'},
    {'name': 'Flickr', 'url': 'http://www.flickr.com/<username>'},
    {'name': 'MyOpenID', 'url': 'https://www.myopenid.com'},
    {'name': 'Facebook', 'url': 'facebook'},
    {'name': 'Twitter', 'url': 'twitter'}]

# this is application database
# SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
if os.environ.get('DATABASE_URL') is None:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
else:
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']

# repo for the scripts needed to upgrade the database for any changes
# in the models
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = "False"
SQLALCHEMY_RECORD_QUERIES = True
# slow database query threshold (in seconds)
DATABASE_QUERY_TIMEOUT = 0.5

# email server
# smtp.googlemail.com
if os.environ.get('HEROKU') is not None:
    SECURITY_PASSWORD_SALT = os.environ.get('app_pass_salt')
    SECRET_KEY = os.environ.get('app_secret')
    MAIL_SERVER = os.environ.get('SMTP_SERVER')
    MAIL_PORT = os.environ.get('SMTP_PORT')
    MAIL_USERNAME = os.environ.get('SMTP_USERNAME')
    MAIL_PASSWORD = os.environ.get('SMTP_PASSWORD')
    # microsoft translation service
    MS_TRANSLATOR_CLIENT_ID = os.environ.get('translator_id')
    MS_TRANSLATOR_CLIENT_SECRET = os.environ.get('translator_secret')
    ADMINS = [os.environ.get('MAIL_DEFAULT_SENDER')]

    OAUTH_CREDENTIALS = {
    'facebook': {
        'id': os.environ.get('FACEBOOKID'),
        'secret': os.environ.get('FACEBOOKSECRET')
    },
    'twitter': {
        'id': os.environ.get('TWITTERID'),
        'secret': os.environ.get('TWITTERSECRET')
    }
    }

else:
    clientsecrets = json.loads(open("{}/etc/clientsecret.json".format(basedir)).read())
    OAUTH_CREDENTIALS = clientsecrets
    SECURITY_PASSWORD_SALT = config["app_pass_salt"]
    SECRET_KEY = config["app_secret"]
    MAIL_SERVER = config['smtp_server']
    MAIL_PORT = config['smtp_port']
    MAIL_USERNAME = config['smtp_username']
    MAIL_PASSWORD = config['smtp_password']
    # microsoft translation service
    MS_TRANSLATOR_CLIENT_ID = config['translator_id']
    MS_TRANSLATOR_CLIENT_SECRET = config['translator_secret']
    # administrator list
    ADMINS = [config['mail_default_sender']]

MAIL_USE_TLS = False
MAIL_USE_SSL = True

# pagination
POSTS_PER_PAGE = 5
COMMENTS_PER_POST = 10

WHOOSH_BASE = os.path.join(basedir, 'search.db')
MAX_SEARCH_RESULTS = 50
FLASKY_COMMENTS_PER_PAGE = 10

LANGUAGES = {
    'en': 'English',
    'es': 'Español'
}

# Whoosh does not work on Heroku
WHOOSH_ENABLED = os.environ.get('HEROKU') is None