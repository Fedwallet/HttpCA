#!/usr/bin/python
#-*- coding: UTF-8 -*-

# Copyright (c) 2013, Patrick Uiterwijk <puiterwijk@gmail.com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of Patrick Uiterwijk nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL Patrick Uiterwijk BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

## These two lines are needed to run on EL6
__requires__ = ['SQLAlchemy >= 0.7', 'jinja2 >= 2.4']
import pkg_resources

# Imports
import flask
from flask.ext.sqlalchemy import SQLAlchemy
from flaskext.babel import Babel

import logging
import logging.handlers

from uuid import uuid4 as uuid
import sys


# Create the application
app = flask.Flask(__name__)
# Set up logging (https://fedoraproject.org/wiki/Infrastructure/AppBestPractices#Centralized_logging)
FORMAT = '%(asctime)-15s HttpCA[%(process)d] %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('httpca')
logger.setLevel(logging.DEBUG)
handler = logging.handlers.SysLogHandler(address='/dev/log', facility=logging.handlers.SysLogHandler.LOG_LOCAL4)
logger.addHandler(handler)
def log_create_message(message, info):
    if not 'log_id' in get_session():
        get_session()['log_id'] = uuid().hex
        get_session().save()
    other = ''
    for key, value in info.iteritems():
        other = '%(other)s, %(key)s=%(value)s' % {'other': other, 'key': key, 'value': value}
    return '%(message)s: sessionid=%(sessionid)s%(other)s' % {'message': message, 'sessionid': get_session()['log_id'], 'other': other}

def log_debug(message, info={}):
    logger.debug(log_create_message(message, info))

def log_info(message, info={}):
    logger.info(log_create_message(message, info))

def log_warning(message, info={}):
    logger.warning(log_create_message(message, info))

def log_error(message, info={}):
    logger.error(log_create_message(message, info))

def get_session():
    return flask.request.environ['beaker.session']

app.config.from_object('httpca_web.default_config')
app.config.from_envvar('HTTPCA_WEB_CONFIG', silent=True)

# Make sure the configuration is sane
if not app.config['SQLALCHEMY_DATABASE_URI']:
    print 'Error: Please make sure to configure SQLALCHEMY_DATABASE_URI'
    sys.exit(1)
if app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite') and bool(app.config['USE_BEAKER']):
    print 'Error: HttpCA-Web does not support sqlite if beaker is enabled'
    sys.exit(1)
if app.config['SQLALCHEMY_DATABASE_URI'].startswith('postgres:'):
    print 'Error: Please use the postgresql dialect (postgresql: instead of postgres: in the database URI)'
    sys.exit(1)
if not app.config['SECRET_KEY'] or app.config['SECRET_KEY'] == 'Secret Key':
    print 'Error: Please make sure to configure SECRET_KEY'
    sys.exit(1)

# Set up SQLAlchemy
db = SQLAlchemy(app)
# Set up Babel
babel = Babel(app)
# Set up sessions
if bool(app.config['USE_BEAKER']):
    from beaker.middleware import SessionMiddleware
    session_opts = {
        'session.lock_dir': '/tmp/beaker',
        'session.type': 'ext:database',
        'session.url': app.config['SQLALCHEMY_DATABASE_URI'],
        'session.auto': False,
        'session.cookie_expires': True,
        'session.key': 'HTTPCA_WEB',
        'session.secret': app.config['SECRET_KEY'],
        'session.secure': False,
        'session.table_name': 'session'
    }
    app.wsgi_app = SessionMiddleware(app.wsgi_app, session_opts)

# Import the other stuff
import model
import views
