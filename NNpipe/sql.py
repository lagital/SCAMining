""" Module containing SQL operations for NNpipe """

import MySQLdb as mdb
import sys
import sql
import config

def open_connection():
	connection = mdb.connect(config.SQL_HOST, config.SQL_USER, config.SQL_PASSWORD, config.SQL_DB)
	return connection

def close_connection(connection):
	connection.close()

def drop_k_weigths(connection):
	cursor = connection.cursor()
	cursor.execute("update K set weight = NULL")
	connection.commit()

def drop_c_weigths(connection):
	cursor = connection.cursor()
	cursor.execute("update C set weight = NULL")
	connection.commit()
	
def drop_training_iterations(connection):
	cursor = connection.cursor()
	cursor.execute("truncate table ITERATION_TRAINING")
	connection.commit()
