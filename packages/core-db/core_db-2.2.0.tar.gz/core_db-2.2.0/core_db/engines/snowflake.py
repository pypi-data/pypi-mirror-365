# -*- coding: utf-8 -*-

import json
from typing import Dict
from typing import List
from typing import Optional
from typing import overload

import snowflake.connector

from core_db.interfaces.sql_based import ISqlDatabaseClient


class SnowflakeClient(ISqlDatabaseClient):
    """ Client to connect to Snowflake Data Warehouse """

    type_mapper = {
        int: "INTEGER",
        float: "DOUBLE",
        str: "VARCHAR",
        bool: "BOOLEAN",
        dict: "OBJECT",
        list: "VARIANT"
    }

    def __init__(self, **kwargs):
        """
        :param kwargs:
            * user: Username.
            * host: Hostname.
            * account: Account name.
            * password: Password.
            * warehouse: Warehouse.
            * database: Database.
            * schema: Schema.
            * role: Role.

        To connect using OAuth, the connection string must include the authenticator parameter set
        to oauth and the token parameter set to the oauth_access_token.
        https://docs.snowflake.com/en/user-guide/python-connector-example.html#connecting-with-oauth

        :param authenticator="oauth"
        :param token="oauth_access_token"
        """

        super().__init__(**kwargs)
        self.connect_fcn = snowflake.connector.connect
        self.epoch_to_timestamp_fcn = "TO_TIMESTAMP"

    def test_connection(self, query: str = None):
        return super().test_connection(query or "SELECT current_version();")

    @classmethod
    def get_insert_dml(cls, table_fqn: str, columns: List, records: List[Dict]) -> str:
        if not records:
            return ""

        select_statement = ", ".join([
            f"PARSE_JSON(Column{pos + 1}) AS {column}"
            if isinstance(records[0][column], list) or isinstance(records[0][column], dict)
            else f"Column{pos + 1} AS {column}"
            for pos, column in enumerate(columns)
        ])

        return f"""
            INSERT INTO {table_fqn}
            SELECT {select_statement}
            FROM VALUES {', '.join(cls._get_values_statement(columns, records))};"""

    @classmethod
    @overload
    def get_merge_dml(
            cls, target: str, columns: List[str], pk_ids: List[str], records: Optional[List[Dict]] = None,
            epoch_column: Optional[str] = None) -> str:
        """ Use this one when the source is a table """

    @classmethod
    @overload
    def get_merge_dml(
            cls, target: str, columns: List[str], pk_ids: List[str], source: Optional[str] = None,
            epoch_column: Optional[str] = None) -> str:
        """ Use this one when the source is a list of records """

    @classmethod
    def get_merge_dml(
            cls, target: str, columns: List[str], pk_ids: List[str], records: Optional[List[Dict]] = None,
            source: Optional[str] = None, epoch_column: Optional[str] = None) -> str:

        source_key = source or "source"
        on_sts = " AND ".join([f"NVL({source_key}.{key}, '') = NVL({target}.{key}, '')" for key in pk_ids])
        matched_and = f"AND {source_key}.{epoch_column} > {target}.{epoch_column} " if epoch_column else ""

        all_columns = pk_ids + columns
        if epoch_column:
            all_columns.extend([epoch_column])

        all_columns = sorted(set(all_columns))
        set_statement = [f"{key} = {source_key}.{key}" for key in all_columns if key not in pk_ids]

        source = source
        if not source:
            source = f"""(
                    SELECT * FROM (
                        VALUES
                        {', '.join(cls._get_values_statement(columns, records))}
                    ) AS source({', '.join(all_columns)})
                ) AS source"""

        return f"""
            MERGE INTO {target}
            USING {source}
            ON {on_sts}
            WHEN MATCHED {matched_and}THEN
            UPDATE SET {', '.join(set_statement)}
            WHEN NOT MATCHED THEN
            INSERT ({', '.join(all_columns)})
            VALUES ({', '.join([f'{source_key}.{key}' for key in all_columns])});"""

    @staticmethod
    def _get_values_statement(columns: List[str], records: List[Dict]) -> List:
        values = []
        for record in records:
            tmp = []
            for key in columns:
                value = record[key]

                tmp.append(
                    f"'{json.dumps(value)}'" if isinstance(value, list) or isinstance(value, dict)
                    else f"'{value}'" if isinstance(value, str)
                    else str(value)
                )

            values.append(f"({', '.join(tmp)})")

        return values
