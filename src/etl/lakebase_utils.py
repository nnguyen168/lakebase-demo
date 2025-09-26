from databricks.sdk import WorkspaceClient
import uuid

import psycopg
from psycopg_pool import ConnectionPool

import pandas as pd

w = WorkspaceClient()

class CustomConnection(psycopg.Connection):
    def __init__(self, *args, instance_name=None, **kwargs):
        self.instance_name = instance_name
        super().__init__(*args, **kwargs)

    @classmethod
    def connect(cls, conninfo='', instance_name=None, **kwargs):
        cred = w.database.generate_database_credential(request_id=str(uuid.uuid4()), instance_names=[instance_name])
        kwargs['password'] = cred.token
        return super().connect(conninfo, **kwargs)

class LakebaseConnection:
    def __init__(self, username, instance_name):
        self.username = username
        self.instance_name = instance_name
        self.pool = self._get_lakebase_connection_pool()

    def _get_lakebase_connection_pool(self):
        instance = w.database.get_database_instance(name=self.instance_name)
        host = instance.read_write_dns
        port = 5432
        database = "databricks_postgres"

        pool = ConnectionPool(
            conninfo=f"dbname={database} user={self.username} host={host}",
            connection_class=CustomConnection,
            kwargs={"instance_name": self.instance_name},
            min_size=1,
            max_size=10,
            open=True
        )
        return pool

    def execute_statement(self, sql):
        with self.pool.connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql)

    def execute_query(self, sql):
        with self.pool.connection() as conn:
            with conn.cursor() as cursor:
                return pd.read_sql_query(sql, conn)
