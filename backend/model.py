#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 22 23:41:14 2022

@author: eusebio
"""
import sys
from flask import Flask
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_compress import Compress # Gzip asnswers
import  sqlalchemy.dialects.postgresql as postgre

db = SQLAlchemy()

def configure_database(app):
    
    db.app = app
    db.init_app(app)
    db.app.app_context().push()
    Migrate(app, db)
    db.create_all()

    @app.before_first_request
    def initialize_database():
        db.create_all()

    @app.teardown_request
    def shutdown_session(exception=None):
        db.session.remove()
        
def create_app(config_mode):
    print("SQLALCHEMY_DATABASE_URI::>'"+str(config_mode.SQLALCHEMY_DATABASE_URI)+"'", flush=True, file=sys.stdout)
    app = Flask(__name__, static_folder="static", template_folder='templates')
    app.config.from_object(config_mode)
    Compress(app)
    configure_database(app)
    CORS(app)
    return app

######################################
######################################
######                          ######
######        Productos         ######
######                          ######
######                          ######
######################################
######################################

class Productos(db.Model):

    __tablename__ = 'Productos'

    id             = db.Column(postgre.INTEGER, primary_key=True,autoincrement=True)
    copyright      = db.Column(postgre.BOOLEAN, default=None, nullable=True)
    title          = db.Column(postgre.VARCHAR(250), default=None, nullable=True)
    imagename      = db.Column(postgre.VARCHAR(250), default=None, nullable=True)
    datecreated    = db.Column(postgre.TIMESTAMP(timezone=False), default=db.func.current_timestamp(), nullable=False)
    datemodified   = db.Column(postgre.TIMESTAMP(timezone=False), default=db.func.current_timestamp(), onupdate=db.func.current_timestamp(), nullable=False)
    datedeleted    = db.Column(postgre.TIMESTAMP(timezone=False), default=None, nullable=True)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            if hasattr(value, '__iter__') and not isinstance(value, str):
                value = value[0]
            setattr(self, property, value)

    def __repr__(self):
        return str(self.title)

######################################
######################################
######                          ######
######      Sistema Debug       ######
######                          ######
######                          ######
######################################
######################################

class DebugTable(db.Model):

    __tablename__ = 'DebugTable'

    id              = db.Column(postgre.INTEGER, primary_key=True, autoincrement=True)
    Fecha           = db.Column(postgre.TIMESTAMP(timezone=False), nullable=False, default=db.func.current_timestamp())
    Type            = db.Column(postgre.VARCHAR(250), nullable=True, default=None, unique=False)
    username        = db.Column(postgre.VARCHAR(250), nullable=True, default=None, unique=False)
    IpAddress       = db.Column(postgre.VARCHAR(250), default=None, nullable=True, unique=False)
    Agent           = db.Column(postgre.VARCHAR(250), default=None, nullable=True, unique=False)
    Browser         = db.Column(postgre.VARCHAR(250), default=None, nullable=True, unique=False)
    BrowserVersion  = db.Column(postgre.VARCHAR(250), default=None, nullable=True, unique=False)
    OperatingSystem = db.Column(postgre.VARCHAR(250), default=None, nullable=True, unique=False)
    OperatingSystemVersion = db.Column(postgre.VARCHAR(250), default=None, nullable=True, unique=False)
    authenticated   = db.Column(postgre.VARCHAR(250), nullable=True, default=None, unique=False)
    FileName        = db.Column(postgre.VARCHAR(250), nullable=True, default=None, unique=False)
    Class           = db.Column(postgre.VARCHAR(250), nullable=True, default=None, unique=False)
    Function        = db.Column(postgre.VARCHAR(250), nullable=True, default=None, unique=False)
    Section         = db.Column(postgre.VARCHAR(250), nullable=True, default=None, unique=False)
    LineNumber      = db.Column(postgre.VARCHAR(250), nullable=True, default=None, unique=False)
    Line            = db.Column(postgre.VARCHAR(250), nullable=True, default=None, unique=False)
    RutasCodigo     = db.Column(postgre.VARCHAR(250), nullable=True, default=None, unique=False)
    Content         = db.Column(postgre.VARCHAR(250), nullable=True, default=None, unique=False)
    datecreated     = db.Column(postgre.TIMESTAMP(timezone=False), nullable=False, default=db.func.current_timestamp())
    datemodified    = db.Column(postgre.TIMESTAMP(timezone=False), nullable=False, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    datedeleted     = db.Column(postgre.TIMESTAMP(timezone=False), nullable=True, default=None)
    
    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            if hasattr(value, '__iter__') and not isinstance(value, str):
                value = value[0]
            setattr(self, property, value)

    def __repr__(self):
        return str(self.Content)
