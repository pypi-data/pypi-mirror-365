# -*- coding: utf-8 -*-

from abc import ABC
from typing import Any
from typing import Dict
from typing import Iterator

try:
    from typing import Self

except ImportError:
    # For earlier versions...
    from typing_extensions import Self

from core_mixins.interfaces.factory import IFactory


class IDatabaseClient(IFactory, ABC):
    """ Base class for all database clients """

    # Mapper for python types to database types...
    type_mapper = {}

    def __init__(self, **kwargs):
        self.cxn_parameters = kwargs
        self.cursor = None
        self.cxn = None

        # Function used by the library to perform
        # the connection to the engine...
        self.connect_fcn = None

    def __enter__(self) -> Self:
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.commit()
        self.close()

    @classmethod
    def registration_key(cls) -> str:
        return cls.__name__

    def connect(self) -> None:
        """ It creates the connection """

        try:
            self.cxn = self.connect_fcn(**self.cxn_parameters)

        except Exception as error:
            raise DatabaseClientException(error)

    def test_connection(self, query: str):
        """ Tests the connection """

    def execute(self, query, **kwargs):
        """ It executes a query in the engine """

    def commit(self) -> None:
        """ It applies the changes """

    def fetch_records(self) -> Iterator[Dict[str, Any]]:
        """ Returns the records """

    def close(self):
        """ It releases resources """

        if self.cxn:
            self.cxn.close()


class DatabaseClientException(Exception):
    """ Custom exception for Database Client """
