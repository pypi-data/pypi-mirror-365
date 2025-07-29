# -*- coding: utf-8 -*-

import json
from abc import ABC
from typing import Any
from typing import Dict
from typing import Iterator
from typing import List
from typing import Optional
from typing import Tuple
from typing import overload

from core_mixins.utils import get_batches

from core_db.interfaces.base import DatabaseClientException
from .base import IDatabaseClient


class ISqlDatabaseClient(IDatabaseClient, ABC):
    """ Base class for all SQL-based database clients """

    type_mapper = {
        int: "INTEGER",
        float: "DOUBLE",
        str: "TEXT",
        bool: "BOOLEAN",
        dict: "JSON",
        list: "JSON"
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Function used by the Database Engine
        # to convert to timestamp...
        self.epoch_to_timestamp_fcn = None

    def test_connection(self, query: str = None):
        try:
            return self.execute(query or "SELECT version()  AS version;")

        except Exception as error:
            raise DatabaseClientException(error)

    def execute(self, query: str, **kwargs):
        if not self.cxn:
            raise DatabaseClientException("There is not an active connection!")

        try:
            if not self.cursor:
                self.cursor = self.cxn.cursor()

            return self.cursor.execute(query)

        except Exception as error:
            raise DatabaseClientException(error)

    def commit(self) -> None:
        self.cxn.commit()

    def columns(self):
        return [
            x[0] for x in self.cursor.description
        ] if self.cursor else []

    def fetch_record(self) -> Dict[str, Any]:
        res = self.fetch_one()
        return dict(zip(self.columns(), res)) if res else None

    def fetch_one(self) -> Tuple:
        return self.cursor.fetchone()

    def fetch_records(self) -> Iterator[Dict[str, Any]]:
        """
        Because the fetchall operation returns a list of tuples (no headers), you
        can use this function to retrieve the data in the form
        of dictionaries...
        """

        headers = self.columns()
        for row in self.fetch_all():
            yield dict(zip(headers, row))

    def fetch_all(self) -> Iterator[Tuple]:
        for row in self.cursor.fetchall():
            yield row

    @classmethod
    def get_create_table_ddl(
            cls, table_fqn: str, columns: List[Tuple[str, Any]],
            temporal: bool = False) -> str:

        """
        Returns the SQL statement to create a table...

        :param table_fqn: Table's full qualifier name.
        :param columns: List of tuples defining the name and data type for the attribute...
        :param temporal: Defines if is a temporal table.

        :return: The query statement.
        """

        # TODO: this function must be improved. Adding PK, unique, etc...

        columns_def = ", ".join([
            f"{name} {cls.type_mapper.get(type_, 'VARCHAR')}"
            for name, type_ in columns
        ])

        return f"CREATE{' TEMPORARY' if temporal else ''} TABLE {table_fqn} ({columns_def});"

    def insert_records(
            self, table_fqn: str, columns: List[str], records: List[Dict],
            records_per_request: int = 500) -> int:

        """
        It removes the complexity of inserting a batch of records managing batches and
        avoid repeating the same code...

        :param table_fqn: Table's fully qualified name (FQN).
        :param columns: List of columns.
        :param records: Records to insert.
        :param records_per_request: Number of records to insert per call.

        :return: Return the number of inserted records.
        """

        if records:
            try:
                total = 0
                for chunk_ in get_batches(records, records_per_request):
                    query = self.get_insert_dml(table_fqn, columns, chunk_)
                    self.execute(query)
                    total += self.cursor.rowcount

                return total

            except Exception as error:
                raise DatabaseClientException(error)

        return 0

    @staticmethod
    def get_insert_dml(table_fqn: str, columns: List[str], records: List[Dict]) -> str:
        """
        Create the query for the INSERT statement.

        :param table_fqn: Table's fully qualified name (FQN).
        :param columns: List of columns.
        :param records: List of records.
        :return: Query.
        """

        if not records:
            return ""

        values = []
        for record in records:
            tmp = [json.dumps(record[key]).replace('"', "'") for key in columns]
            values.append(f"({', '.join(tmp)})")

        return f"""INSERT INTO {table_fqn} ({', '.join(columns)}) VALUES {', '.join(values)}"""

    @staticmethod
    @overload
    def get_delete_dml(
            table_fqn: str, *, pk_id: Optional[str] = None,
            ids: Optional[List] = None) -> str:
        """ Use this method when you provide the ids """

    @staticmethod
    @overload
    def get_delete_dml(
            table_fqn: str, *, pk_id: Optional[str] = None,
            conditionals: Optional[List[Dict]] = None) -> str:
        """ Use this method when you have multiple conditionals """

    @staticmethod
    def get_delete_dml(
            table_fqn: str, *, pk_id: Optional[str] = None, ids: Optional[List] = None,
            conditionals: Optional[List[Dict]] = None) -> str:

        """ Creates the DELETE statement """

        if pk_id:
            in_statement = ", ".join(
                [f"{json.dumps(rec[pk_id])}" for rec in conditionals]
                if conditionals else [repr(id_) for id_ in ids])

            return f"DELETE FROM {table_fqn} " \
                   f"WHERE {pk_id} " \
                   f"IN ({in_statement})".replace('"', "'")

        statements = []
        for conditional in conditionals:
            statements.append(
                " AND ".join([
                    f"{key} = '{conditional[key]}'"
                    for key in conditionals[0].keys()
                ])
            )

        return f"DELETE FROM {table_fqn} WHERE {' OR '.join([f'({sts})' for sts in statements])}"

    @staticmethod
    def get_merge_dml(*args, **kwargs) -> str:
        """ It returns the merge statement """
