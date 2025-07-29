# -*- coding: utf-8 -*-

from typing import Iterator, Dict, Any, Tuple

import ibm_db

from core_db.interfaces.base import DatabaseClientException
from core_db.interfaces.sql_based import ISqlDatabaseClient


class Db2Client(ISqlDatabaseClient):
    """
    Client for IBM DB2 database connection...

    ===================================================
    How to use
    ===================================================

    .. code-block:: python

        from core_db.engines.db2 import Db2Client

        dsn_hostname, dsn_port, dsn_database = "localhost", "50000", "sample"
        dsn_uid, dsn_pwd = "db2inst1", "SomePassword"

        dsn = (
            f"DATABASE={dsn_database};"
            f"HOSTNAME={dsn_hostname};"
            f"PORT={dsn_port};"
            f"PROTOCOL=TCPIP;"
            f"UID={dsn_uid};"
            f"PWD={dsn_pwd};")

        with Db2Client(dsn=dsn, user="", password="") as client:
            client.execute("select * from department FETCH FIRST 2 ROWS ONLY;")
            print(client.fetch_one())
            print(client.fetch_record())
    ..
    """

    def __init__(self, dsn: str, user: str = "", password: str = "", **kwargs):
        super(Db2Client, self).__init__(dsn=dsn, user=user, password=password, **kwargs)
        self.connect_fcn = ibm_db.connect
        self.statement = None

    def connect(self) -> None:
        try:
            self.cxn = self.connect_fcn(
                self.cxn_parameters.get("dsn", ""),
                self.cxn_parameters.get("user", ""),
                self.cxn_parameters.get("password", ""))

        except Exception as error:
            raise DatabaseClientException(error)

    def test_connection(self, query: str = None):
        return self.execute(query or "SELECT * FROM SYSIBMADM.ENV_SYS_INFO FETCH FIRST 2 ROWS ONLY;")

    def execute(self, query: str, **kwargs):
        self.statement = ibm_db.exec_immediate(self.cxn, query)

    def commit(self) -> None:
        ibm_db.commit(self.cxn)

    def fetch_record(self) -> Dict[str, Any]:
        return ibm_db.fetch_assoc(self.statement)

    def fetch_one(self) -> Tuple:
        return ibm_db.fetch_tuple(self.statement)

    def fetch_records(self) -> Iterator[Dict[str, Any]]:
        while row_ := ibm_db.fetch_assoc(self.statement):
            yield row_

    def fetch_all(self) -> Iterator[Tuple]:
        while row_ := ibm_db.fetch_tuple(self.statement):
            yield row_

    def close(self):
        ibm_db.close(self.cxn)
