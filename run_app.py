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

from flask import Flask
from flask import request
from werkzeug.exceptions import NotFound
from flask_restplus import Api, Resource, fields
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Integer
from flask_marshmallow import Marshmallow

logger = logging.getLogger(__name__)


def get_config_parameter(env_var, default):
    parameter = (os.getenv(env_var) or default)
    logger.debug('Parameter %s = %s' % (env_var, parameter))
    return parameter


def get_database_connection():
    """ This uses environment variables to pass DB settings and defaults to in-memory sqlite.

        For more info see, https://www.habitat.sh/docs/using-habitat/#config-updates
        e.g. HAB_PACKAGENAME='{"keyname1":"newvalue1", "tablename1":{"keyname2":"newvalue2"}}'

        DB_TYPE = sqlite_in_memory / sqlite_file / ...
    """

    db_type = get_config_parameter('DB_TYPE', 'sqlite_in_memory')
    logger.info("Using %s database" % db_type)

    if db_type == 'sqlite_in_memory':
        return 'sqlite://'

    if db_type == 'sqlite_file':
        return 'sqlite:///table_setting.db'

    if db_type == 'mysql':
        # this is brittle, should revisit
        db_user = get_config_parameter('DB_USER', 'root')
        db_passwd = get_config_parameter('DB_PASSWD', '')
        db_host = get_config_parameter('DB_HOST', '127.0.0.1')
        db_port = get_config_parameter('DB_PORT', '3306')
        db_name = get_config_parameter('DB_NAME', 'tablesetting')
        return 'mysql://%s:%s@%s:%s/%s' % (db_user, db_passwd, db_host, db_port, db_name)

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
    # bootstrap DB if we are running in-memory mode
    if 'db_mysql' not in os.environ:
        logger.info('Bootstrapping in-memory DB')
        database.create_all()


api = Api(app, version='0.0.1', title='Table Setting API',
          description='Swagger API for Table Setting, the best (and probably only) way to REST API your forks.'
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
    app.run(debug=True, port=port_number)
