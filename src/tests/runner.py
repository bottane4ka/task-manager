from types import MethodType
from django.test.runner import DiscoverRunner
from django.db import connections
from settings import BASE_ROOT_DIR
from pathlib import Path


def prepare_database(db):
    db.connect()
    cursor = db.connection.cursor()
    for data in get_sql(["first_create.sql", "notify_procedure.sql"]):
        cursor.execute(data)


def get_sql(sql_script):
    main_path = Path(BASE_ROOT_DIR) / "db"
    for path in sql_script:
        with open(main_path / path, "r") as f:
            yield f.read()


class PostgresSchemaTestRunner(DiscoverRunner):

    def setup_databases(self, **kwargs):
        for connection_name in connections:
            connection = connections[connection_name]
            connection.prepare_database = MethodType(prepare_database, connection)
        return super().setup_databases(**kwargs)
