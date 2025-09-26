from databricks.sdk import WorkspaceClient
import uuid

import psycopg
from psycopg_pool import ConnectionPool
from psycopg2.errors import DuplicateObject

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

    def create_role_with_permissions(self, role_name, password):
        with self.pool.connection() as conn:
            with conn.cursor() as cursor:
                try:
                    cursor.execute(f"CREATE ROLE {role_name} LOGIN PASSWORD '{password}'")
                    cursor.execute(f"GRANT CONNECT ON DATABASE databricks_postgres TO {role_name}")
                    cursor.execute(f"GRANT USAGE ON SCHEMA public TO {role_name}")
                    cursor.execute(f"GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO {role_name}")
                    cursor.execute(f"GRANT CREATE ON SCHEMA public to {role_name}")
                    cursor.execute(f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO {role_name}")
                    cursor.execute(f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE ON SEQUENCES TO {role_name}")
                    print(f"Role {role_name} created with permissions")
                except DuplicateObject:
                    print(f"Role {role_name} already exists")
                except Exception as e:
                    print(f"Error creating role {role_name}: {e}")
