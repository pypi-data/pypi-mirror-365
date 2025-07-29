# -*- coding: utf-8 -*-

from __future__ import annotations

from abc import ABC, abstractmethod
from logging import Logger
from re import compile
from typing import List, Tuple

try:
    from typing import Self

except ImportError:
    # For earlier versions...
    from typing_extensions import Self

from core_mixins.interfaces.factory import IFactory
from pymysqlreplication.event import QueryEvent

from core_cdc.base import Record


class ITarget(IFactory, ABC):
    """
    This is the base class for the specific implementations of
    the targets the data will be sent or replicated. A target could
    be a database, queue, topic, data warehouse, etc...
    """

    def __init__(
            self, logger: Logger, execute_ddl: bool = False,
            send_data: bool = False,
            **kwargs) -> None:

        self.execute_ddl = execute_ddl
        self.send_data = send_data
        self.logger = logger
        self.client = None

    @classmethod
    def registration_key(cls) -> str:
        return cls.__name__

    def init_client(self, **kwargs) -> None:
        """ The target's implementations must implement this method """

    def connect(self) -> None:
        if self.client:
            self.client.connect()

    def get_ddl_query(self, event: QueryEvent) -> str:
        """
        Each engine could use a different query for DDL operations...
        :return: The query or None if not supported.
        """

        # sql_statement = sub(r"/\*.*?\*/", "", event.query.lower()).strip()
        sql_statement = event.query.lower()

        if sql_statement.count("create schema") or sql_statement.count("create database"):
            return self.get_create_schema_statement(event)

        elif sql_statement.count("drop schema") or sql_statement.count("drop database"):
            return self.get_drop_schema_statement(event)

        elif sql_statement.count("create table"):
            return self.get_create_table_statement(event)

        elif sql_statement.count("alter table"):
            return self.get_alter_table_statement(event)

        elif sql_statement.count("drop table"):
            return self.get_drop_table_statement(event)

        return ""

    @staticmethod
    def get_add_column_ddl(schema: str, table: str, column: str, type_: str) -> str:
        """ Returns the DDL to add a new column """
        return f"ALTER TABLE `{schema}`.`{table}` ADD COLUMN `{column}` {type_};"

    @staticmethod
    def get_create_schema_statement(event: QueryEvent) -> str:
        return event.query

    @staticmethod
    def get_drop_schema_statement(event: QueryEvent) -> str:
        return event.query

    @staticmethod
    def get_create_table_statement(event: QueryEvent) -> str:
        return event.query

    @staticmethod
    def get_alter_table_statement(event: QueryEvent) -> str:
        return event.query

    @staticmethod
    def get_schema_table_from_query(query: str) -> Tuple[str, str]:
        """ Returns schema, table from query using Regex """

        # TODO if the query does not contains "`" this will not work...
        data = compile("`[a-z_]+`.`[a-z_]+`").search(query).group(0)
        schema, table = data.replace("`", "").split(".")
        return schema, table

    @staticmethod
    def get_drop_table_statement(event: QueryEvent) -> str:
        return event.query

    def execute(self, query: str):
        if self.client:
            self.client.execute(query)

    def save(self, records: List[Record], **kwargs):
        if self.send_data:
            self._save(records, **kwargs)
            self.logger.info(f"{len(records)} records were sent to: {self.registration_key()}!")

    @abstractmethod
    def _save(self, records: List[Record], **kwargs):
        """ Specific implementation to store the data into the Engine """

    def close(self):
        """ Implement it if is required to release or close resources """
