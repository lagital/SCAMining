""" Configuration file for NNpipe """

DEBUG = True

WAV_EXTENTION = ".wav"
SIG_INFO_EXTENSION = "_info.txt"
NN_OUTPUT_EXTENTION = "_result.txt"

#drop C weigths before start learning
DROP_C_WEIGHTS_ON_START = True
#drop K weigths before start learning
DROP_K_WEIGHTS_ON_START = True
#drop ITERATION_TRAINIG content before start learning
DROP_ITERATIONS_TRAIN_ON_START = True
#continue learning even during attacking
UPDATE_WEIGTHS_IN_ATTACKS = True

DEVICE_SAMPLING = 44100
TIMESTAMP_SAMPLING = 1000000000

#SQL connect parameters
SQL_HOST = "test_host"
SQL_DB = "test_db_name"
SQL_USER = "test_user"
SQL_PASSWORD = "test_password"
