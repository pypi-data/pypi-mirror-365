# -*- coding: utf-8 -*-

from __future__ import annotations

from abc import ABC
from typing import Dict, Iterator, Any, List

from core_etl.record_based import IBaseEtlFromRecord

from core_db.interfaces.base import IDatabaseClient


class IBaseEtlFromDatabase(IBaseEtlFromRecord, ABC):
    """
    Base class for those ETL processes that retrieves data from a database
    and process every record...
    """

    def __init__(
            self, database_type: str, connection_parameters: Dict,
            base_query: str = None, **kwargs):

        """
        :param database_type: The name of the class that defines the database connection.
        :param connection_parameters: The parameters to create the database connection.
        :param base_query: Query base to use when retrieving data.
        """

        super(IBaseEtlFromDatabase, self).__init__(**kwargs)

        self.database_type = database_type
        self.connection_parameters = connection_parameters
        self.db_client: IDatabaseClient | None = None
        self.base_query = base_query

    def pre_processing(self, **kwargs) -> None:
        super(IBaseEtlFromDatabase, self).pre_processing(**kwargs)

        database_cls = IDatabaseClient.get_class(self.database_type)
        self.db_client = database_cls(**self.connection_parameters) if database_cls else None
        self.db_client.connect()

    def get_query(self, *args, **kwargs) -> str:
        """ Must return the required query to retrieve the data... """
        return self.base_query

    def retrieve_records(
            self, last_processed: Any = None, start: Any = None,
            end: Any = None, **kwargs) -> Iterator[List[Dict]]:

        """ It retrieves records from sources... """

        self.db_client.execute(
            self.get_query(
                last_processed=last_processed,
                start=start, end=end,
                **kwargs
            )
        )

        batch = []
        for record in self.db_client.fetch_records():
            batch.append(record)
            if len(batch) == self.max_per_batch:
                yield batch
                batch = []

    def process_records(self, records: List[Dict], **kwargs):
        """
        It must implement the actions to do with the records after
        transformations like archive in S3, send to an sFTP server, send to
        an SQS queue or a Kinesis stream...
        """

    def clean_resources(self) -> None:
        self.db_client.close()
