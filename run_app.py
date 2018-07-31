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


def get_database_connection():
    if 'db_mysql' in os.environ:
        logger.info("Using MySQL DB as db_mysql in local environment")
        return os.getenv('db_mysql')

    logger.info("Using in-memory sqlite database")
    return 'sqlite://'


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

    @fork_namespace.response(200, 'Success')
    def get(self):
        return forks_schema.dump(ForkModel.query.all()).data, 200

    @fork_namespace.response(201, 'Success')
    @fork_namespace.expect(fork_request, validate=True)
    def post(self):
        request_json = request.json
        fork = ForkModel(id=str(uuid.uuid4()), name=request_json['name'], prongs=request_json['prongs'])
        database.session.add(fork)
        database.session.commit()
        return fork_schema.dump(fork).data, 201


@fork_namespace.route('/<id>')
class ForkResource(Resource):
    @fork_namespace.response(200, 'Success')
    @fork_namespace.response(404, 'Fork does not exist')
    def get(self, id):
        fork = ForkModel.query.get(id)
        if fork:
            return fork_schema.dump(fork).data, 200
        else:
            return {'message': 'Fork with id %s not found' % id}, 404

    @fork_namespace.response(204, 'Fork updated')
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

    @fork_namespace.response(204, 'Fork deleted')
    def delete(self, id):
        fork = ForkModel.query.get(id)
        if not fork:
            raise NotFound(description=id)
        else:
            database.session.delete(fork)
            database.session.commit()
            return {}, 204


if __name__ == '__main__':
    port_number = 5000
    if 'PORT' in os.environ:
        port_number = int(os.environ['PORT'])

    app.run(debug=True, port=port_number)
