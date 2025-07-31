DB_AUTH_TEMPLATE = """
from dataclasses import dataclass, field
from typing import Optional
import psycopg2
from psycopg2.extensions import connection

@dataclass
class {service_name}Auth:
    host: str
    port: int
    dbname: str
    user: str
    password: str
    connection: Optional[connection] = field(default=None)

    def connect(self) -> connection:
        \"\"\"
        Estabelece conexão com o banco de dados PostgreSQL.
        \"\"\"
        if not self.connection:
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                dbname=self.dbname,
                user=self.user,
                password=self.password
            )
        return self.connection

    def close(self) -> None:
        \"\"\"
        Fecha a conexão com o banco de dados.
        \"\"\"
        if self.connection:
            self.connection.close()
            self.connection = None
"""


DB_SERVICE_TEMPLATE = """
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union
from psycopg2.extensions import connection
from .{service_name_lower}_auth import {service_name}Auth

@dataclass
class QueryOptions:
    where: Optional[Dict[str, Any]] = None
    order_by: Optional[List[str]] = None
    limit: Optional[int] = None
    offset: Optional[int] = None

@dataclass
class {service_name}Service:
    auth: {service_name}Auth

    def get(self, table: str, columns: Optional[List[str]] = None, options: Optional[QueryOptions] = None) -> List[Tuple]:
        \"\"\"
        Busca registros no banco de dados.
        \"\"\"
        conn: connection = self.auth.connect()
        with conn.cursor() as cursor:
            cols = ", ".join(columns) if columns else "*"
            query = f"SELECT {{cols}} FROM {{table}}"
            params = []
            if options and options.where:
                where_clause = " AND ".join([f"{{k}} = %s" for k in options.where.keys()])
                query += f" WHERE {{where_clause}}"
                params.extend(options.where.values())
            if options and options.order_by:
                order_clause = ", ".join(options.order_by)
                query += f" ORDER BY {{order_clause}}"
            if options and options.limit is not None:
                query += f" LIMIT {{options.limit}}"
            if options and options.offset is not None:
                query += f" OFFSET {{options.offset}}"
            cursor.execute(query, params)
            return cursor.fetchall()

    def post(self, table: str, data: Dict[str, Any]) -> None:
        \"\"\"
        Insere um registro no banco de dados.
        \"\"\"
        conn: connection = self.auth.connect()
        with conn.cursor() as cursor:
            columns = ", ".join(data.keys())
            placeholders = ", ".join(["%s"] * len(data))
            query = f"INSERT INTO {{table}} ({{columns}}) VALUES ({{placeholders}})"
            cursor.execute(query, list(data.values()))
            conn.commit()

    def update(self, table: str, data: Dict[str, Any], options: QueryOptions) -> None:
        \"\"\"
        Atualiza registros no banco de dados.
        \"\"\"
        if not options or not options.where:
            raise ValueError("WHERE clause is required for UPDATE to prevent updating all rows.")
        conn: connection = self.auth.connect()
        with conn.cursor() as cursor:
            set_clause = ", ".join([f"{{k}} = %s" for k in data.keys()])
            where_clause = " AND ".join([f"{{k}} = %s" for k in options.where.keys()])
            query = f"UPDATE {{table}} SET {{set_clause}} WHERE {{where_clause}}"
            params = list(data.values()) + list(options.where.values())
            cursor.execute(query, params)
            conn.commit()

    def delete(self, table: str, options: QueryOptions) -> None:
        \"\"\"
        Exclui registros no banco de dados.
        \"\"\"
        if not options or not options.where:
            raise ValueError("WHERE clause is required for DELETE to prevent deleting all rows.")
        conn: connection = self.auth.connect()
        with conn.cursor() as cursor:
            where_clause = " AND ".join([f"{{k}} = %s" for k in options.where.keys()])
            query = f"DELETE FROM {{table}} WHERE {{where_clause}}"
            params = list(options.where.values())
            cursor.execute(query, params)
            conn.commit()
"""

MODEL_TEMPLATE = """
from dataclasses import dataclass
from typing import Optional

@dataclass
class {data_name}:
    {columns}
    
    def to_dict(self) -> dict:
        \"\"\"
        Converte o modelo para um dicionário.
        \"\"\"
        return self.__dict__
"""