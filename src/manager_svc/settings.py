import os
import configparser

BASE_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
config = configparser.ConfigParser()
config_path = "{}/conf/config.ini".format(BASE_DIR)
config.read(config_path)
# Системное наименование модуля
MODULE_SYSTEM_NAME = config["DEFAULT"]["SYSTEM_NAME"]

# Каналы (наименования таблиц), которые слушает служба
MAIN_TASK_LOG_CHANNEL = config["LISTEN_CHANNEL_NAME"]["table_main_task_log"]
TASK_LOG_CHANNEL = config["LISTEN_CHANNEL_NAME"]["table_task_log"]
MESSAGE_CHANNEL = config["LISTEN_CHANNEL_NAME"]["table_message"]
COMMAND_LOG_CHANNEL = config["LISTEN_CHANNEL_NAME"]["table_command_log"]

# Период (в минутах) повторения периодической задачи
PERIOD_TIME = int(config["DEFAULT"]["period_time"])

DB_NAME = config["DATABASE"]["NAME"]
DB_USER = config["DATABASE"]["USER"]
DB_HOST = config["DATABASE"]["HOST"]
DB_PORT = config["DATABASE"]["PORT"]
