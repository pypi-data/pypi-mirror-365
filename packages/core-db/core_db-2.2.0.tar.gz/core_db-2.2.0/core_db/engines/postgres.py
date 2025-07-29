# -*- coding: utf-8 -*-

import json
from typing import Dict, List

import psycopg

from core_db.interfaces.sql_based import ISqlDatabaseClient


class PostgresClient(ISqlDatabaseClient):
    """
    Client for PostgreSQL connection...

    ===================================================
    How to use
    ===================================================

    .. code-block:: python

        from core_db.engines.postgres import PostgresClient

        cxn_info = "postgresql://postgres:postgres@localhost:5432/test"

        with PostgresClient(conninfo=cxn_info) as client:
            client.execute("SELECT version() AS version;")
            print(client.fetch_one()[0])
    ..
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.epoch_to_timestamp_fcn = "TO_TIMESTAMP"
        self.connect_fcn = psycopg.connect

    @staticmethod
    def get_merge_dml(
            table_fqn: str, pk_ids: List[str], columns: List[str],
            records: List[Dict]) -> str:

        rows = [
            str(
                tuple(
                    [
                        json.dumps(value)
                        if type(value) in [dict, list] else value
                        for attr, value in record.items()
                    ]
                )
            ) for record in records
        ]

        set_statement = ", \n".join([f"{column} = EXCLUDED.{column}" for column in columns if column not in pk_ids])
        rows = ", \n".join(rows)

        return f"""
            INSERT INTO {table_fqn} ({', '.join(columns)}) 
            VALUES 
                {rows} 
            ON CONFLICT ({', '.join(pk_ids)}) DO UPDATE 
            SET 
                {set_statement};"""
