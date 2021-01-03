import os
import configparser

BASE_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
config = configparser.ConfigParser()
config_path = "{}/conf/config.ini".format(BASE_DIR)
config.read(config_path)

DB_NAME = config['DATABASE']['NAME']
DB_USER = config['DATABASE']['USER']
DB_HOST = config['DATABASE']['HOST']
DB_PORT = config['DATABASE']['PORT']
