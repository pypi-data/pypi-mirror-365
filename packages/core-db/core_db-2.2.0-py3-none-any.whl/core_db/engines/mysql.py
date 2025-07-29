# -*- coding: utf-8 -*-

import json
from typing import Dict
from typing import List
from typing import Optional

import pymysql

from core_db.interfaces.sql_based import ISqlDatabaseClient


class MySQLClient(ISqlDatabaseClient):
    """
    Client for MySQL connection...

    ===================================================
    How to use
    ===================================================

    .. code-block:: python

        from core_db.engines.mysql import MySQLClient

        with MySQLClient(host="localhost", user="root", password="SomePassword") as client:
            client.execute("SELECT * FROM ...;")

            for x in client.fetch_all():
                print(x)
    ..
    """

    def __init__(self, **kwargs):
        """
        Expected -> host, user, password, database
        More information:
          - https://pymysql.readthedocs.io/en/latest/user/index.html#
          - https://pypi.org/project/PyMySQL/
        """

        super().__init__(**kwargs)
        self.epoch_to_timestamp_fcn = "FROM_UNIXTIME"
        self.connect_fcn = pymysql.connect

    @staticmethod
    def get_merge_dml(
            table_fqn: str, columns: List[str], records: List[Dict],
            epoch_column: Optional[str] = None) -> str:

        """
        Returns the DML statement for merging...

        :param table_fqn: Full qualified name for the target table.
        :param columns: The names of the columns.
        :param records: The list of records you will insert or update.
        :param epoch_column: If exists, only newest records will be updated.
        """

        if epoch_column:
            # Because the column must be at the end...
            columns.remove(epoch_column)
            columns.append(epoch_column)

        rows, recs = [[rec[key] for key in columns] for rec in records], []
        schema, table = table_fqn.split(".")

        for row in rows:
            iter_ = [
                f"'{attr}'" if isinstance(attr, str)
                else f"'{json.dumps(attr)}'" if isinstance(attr, list) or isinstance(attr, dict)
                else str(attr) for attr in row
            ]

            recs.append(f"({', '.join(iter_)})")

        on_duplicate = [
            f"{y}=if(VALUES({epoch_column}) > {epoch_column}, VALUES({y}), {y})"
            if epoch_column else f"{y}=VALUES({y})"
            for y in columns
        ]

        return f"""
            INSERT INTO `{schema}`.`{table}`
            ({', '.join([f'`{x}`' for x in columns])})
            VALUES
            {', '.join(recs)}
            ON DUPLICATE KEY UPDATE
            {', '.join(on_duplicate)};"""
