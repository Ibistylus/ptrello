# -*- coding: utf-8 -*-

import logging
import urllib
import pyodbc as db
from pandas.io.sql import read_sql
from core.config import settings, logger

import sqlalchemy
from sqlalchemy.engine import reflection

logger = logging.getLogger("ptrello."+__name__)



def make_engine(connection_str=None, host_name=None, db_name=None):

    logger.debug(settings['db_connection']['db'])
    DEFAULT_DB_NAME = settings['db_connection']['db']
    DEFAULT_DB_SERVER = settings['db_connection']['host']
    connection=None

    if db_name is None:
        database_name = DEFAULT_DB_NAME
    else:
        database_name = db_name

    if connection_str is None:
        conn_str = "DRIVER={SQL Server}; SERVER=" + DEFAULT_DB_SERVER + "; DATABASE=" + str(database_name)
    else:
        conn_str = connection_str + str(database_name)

    params = urllib.parse.quote_plus("DRIVER={SQL Server};SERVER=VIDEADDQASPRC03;DATABASE=VideaSuperSnapshot")
    engine = sqlalchemy.create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)
    return engine


def get_all_schemas(engine=None):
    if not engine:
        engine = make_engine()

    insp = reflection.Inspector.from_engine(engine)
    return insp.get_schema_names()

def get_all_databases(engine=None):
    if not engine:
        engine = make_engine()

    sql  = """
    select name, database_id from sys.databases
    """

    return  read_sql(sql,engine)


def tutorial(engine=None):
    if not engine:
        engine = make_engine()

    #reflect metadata from engine
    metadata = sqlalchemy.MetaData(engine, reflect=True)

    #prepare a table for selection and select
    table = metadata.tables['BroadcastCalendar']
    select_st = sqlalchemy.select([table]).limit(5)
    res = engine.connect().execute(select_st)

    #prints select statement
    print(select_st)

    #pass select statement and engine to pandas
    df = read_sql(select_st,engine)
