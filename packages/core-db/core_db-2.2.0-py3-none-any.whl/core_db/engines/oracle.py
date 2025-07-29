# -*- coding: utf-8 -*-

import oracledb

from core_db.interfaces.sql_based import ISqlDatabaseClient


class OracleClient(ISqlDatabaseClient):
    """
    Client for Oracle connection...

    ===================================================
    How to use
    ===================================================

    .. code-block:: python

        from core_db.engines.oracle import OracleClient

        with OracleClient(user="...", password="...", dsn=f"{host}:{port}/{service_name}") as client:
            res = client.execute("SELECT * FROM ...")

            for x in client.fetch_all():
                print(x)
    ..
    """

    def __init__(self, **kwargs):
        """
        Expected -> user, password, dsn...

        More information:
          - https://oracle.github.io/python-oracledb/
          - https://python-oracledb.readthedocs.io/en/latest/index.html
        """

        super(OracleClient, self).__init__(**kwargs)
        self.connect_fcn = oracledb.connect

    def test_connection(self, query: str = None):
        if not query:
            query = 'SELECT * FROM "V$VERSION"'

        return super(OracleClient, self).test_connection(query)
