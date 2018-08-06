#!/usr/bin/env python

""" Table Setting

    This is a simple python flask web application developed for demonstration purposes. This uses Flask, Flask-RESTPlus,
     Marshmallow and SQLAlchemy to provide a simple REST API for forks.

    Note that this is very far from a production application:
        - all code is deliberately kept in one file for simplicity
        - Flask runs in DEBUG mode
        - A Swagger UI is served at the default app root '/'
        - DB is in-memory sqlite by default (can override connection string via db_mysql env var)
"""

import logging
import os
import uuid
import sqlalchemy
import warnings
import re

from flask import Flask
from flask import request
from werkzeug.exceptions import NotFound
from flask_restplus import Api, Resource, fields
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Integer
from sqlalchemy.engine import url as db_url
from flask_marshmallow import Marshmallow
from logging.config import dictConfig

# simple default logging borrowed from http://flask.pocoo.org/docs/1.0/logging/
dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

logger = logging.getLogger(__name__)


def get_config_parameter(env_var, default):
    parameter = (os.getenv(env_var) or default)
    # note the below happily logs the DB connection information
    logger.info('Parameter %s = %s' % (env_var, parameter))
    return parameter


def get_database_connection():
    """ This uses environment variables to pass DB settings and defaults to in-memory sqlite.

        For more info see, https://www.habitat.sh/docs/using-habitat/#config-updates
        e.g. HAB_PACKAGENAME='{"keyname1":"newvalue1", "tablename1":{"keyname2":"newvalue2"}}'

        DB_TYPE = ( sqlite_in_memory | sqlite_file | mysql )
    """

    db_type = get_config_parameter('DB_TYPE', 'sqlite_in_memory')
    logger.info("Using %s database" % db_type)

    if db_type == 'sqlite_in_memory':
        return db_url.URL(drivername='sqlite')

    if db_type == 'sqlite_file':
        return db_url.URL(
            drivername='sqlite',
            database=get_config_parameter('DB_NAME', 'table_setting.db'),
        )

    if db_type == 'mysql':
        # this is brittle, should revisit
        return db_url.URL(
            drivername='mysql+mysqldb',
            username=get_config_parameter('DB_USER', 'root'),
            password=get_config_parameter('DB_PASSWD', ''),
            host=get_config_parameter('DB_HOST', '127.0.0.1'),
            port=get_config_parameter('DB_PORT', '3306'),
            database=get_config_parameter('DB_NAME', 'tsdb'),
        )

    raise RuntimeError("Database type %s not recognised, exiting" % db_type)


database = SQLAlchemy()
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = get_database_connection()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config.SWAGGER_UI_DOC_EXPANSION = 'list'
app.config.SWAGGER_UI_OPERATION_ID = True
app.config.SWAGGER_UI_REQUEST_DURATION = True

database.init_app(app)
marshmallow = Marshmallow(app)


# simple DB schema for our cutlery


class ForkModel(database.Model):
    __tablename__ = 'cutlery_fork'

    id = Column(String(64), primary_key=True)
    name = Column(String(255), unique=False, nullable=True)
    prongs = Column(Integer, unique=False, nullable=True)


class ForkSchema(marshmallow.ModelSchema):
    class Meta:
        model = ForkModel


# Below are the fields we want to serialize
only = ('id', 'name', 'prongs')
fork_schema = ForkSchema(only=only)
forks_schema = ForkSchema(many=True, only=only)


@app.before_first_request
def create_database():
    logger.info('Bootstrapping DB')
    # create the DB if it doesn't already exist
    conn = get_database_connection()
    if re.search('mysql', conn.drivername):
        db_name = conn.database
        conn.database = ''
        engine = sqlalchemy.create_engine(conn)  # connect to server
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            engine.execute("CREATE DATABASE IF NOT EXISTS %s" % db_name)  # create db

    database.create_all()
    database.session.commit()


description = 'Swagger API for Table Setting, the best (and probably only) way to REST API your forks.'
description += ' Running with a %s database.' % (get_config_parameter('DB_TYPE', 'sqlite_in_memory'))
api = Api(app, version='0.0.1', title='Table Setting API',
          description=description
          )

api.namespaces.clear()  # to remove the default namespace
fork_namespace = api.namespace("forks", description='Forks namespace operations')

fork_request = api.model('Fork Request', {
    'name': fields.String(required=True, description='Name of the fork'),
    'prongs': fields.Integer(required=True, description='Prongs of the fork'),
})


@fork_namespace.route('/', strict_slashes=False)
class ForksResource(Resource):

    @fork_namespace.response(200, 'Successfully retrieved all the forks')
    def get(self):
        return forks_schema.dump(ForkModel.query.all()).data, 200

    @fork_namespace.response(201, 'Successfully created a fork')
    @fork_namespace.expect(fork_request, validate=True)
    def post(self):
        request_json = request.json
        fork = ForkModel(id=str(uuid.uuid4()), name=request_json['name'], prongs=request_json['prongs'])
        database.session.add(fork)
        database.session.commit()
        return fork_schema.dump(fork).data, 201


@fork_namespace.route('/<id>')
class ForkResource(Resource):
    @fork_namespace.response(200, 'Successfully retrieved a fork')
    @fork_namespace.response(404, 'Fork does not exist')
    def get(self, id):
        fork = ForkModel.query.get(id)
        if fork:
            return fork_schema.dump(fork).data, 200
        else:
            return {'message': 'Fork with id %s not found' % id}, 404

    @fork_namespace.response(204, 'Fork is updated')
    @fork_namespace.expect(fork_request, validate=True)
    def put(self, id):
        request_json = request.json
        fork = ForkModel.query.get(id)
        if not fork:
            raise NotFound(description=id)
        else:
            fork.name = request_json['name']
            fork.prongs = request_json['prongs']
            database.session.commit()
            return {}, 204

    @fork_namespace.response(204, 'Fork is deleted')
    def delete(self, id):
        fork = ForkModel.query.get(id)
        if not fork:
            raise NotFound(description=id)
        else:
            database.session.delete(fork)
            database.session.commit()
            return {}, 204


# todo: add an api endpoint to optionally reset the database
if __name__ == '__main__':
    port_number = get_config_parameter('APP_PORT', 5000)
    flask_host = get_config_parameter('APP_HOST', '0.0.0.0')
    app.run(debug=True, host=flask_host, port=port_number)
