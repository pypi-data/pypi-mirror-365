# -*- coding: utf-8 -*-

from typing import Any, Iterator, List

from pymysqlreplication import BinLogStreamReader
from pymysqlreplication.event import GtidEvent
from pymysqlreplication.event import QueryEvent
from pymysqlreplication.event import RotateEvent
from pymysqlreplication.event import XidEvent
from pymysqlreplication.row_event import DeleteRowsEvent
from pymysqlreplication.row_event import UpdateRowsEvent
from pymysqlreplication.row_event import WriteRowsEvent

from core_cdc.base import Record, EventType
from .base import IProcessor


class MySqlBinlogProcessor(IProcessor):
    """
    It processes the events from the BinLog files.

    The binary log contains “events” that describe database changes such as table creation
    operations or changes to table data. It also contains events for statements that potentially
    could have made changes (for example, a DELETE which matched no rows), unless row-based
    logging is used. The binary log also contains information about how long each
    statement took that updated data.

    More information:
    https://dev.mysql.com/doc/refman/8.0/en/binary-log.html
    """

    def __init__(self, stream: BinLogStreamReader, **kwargs) -> None:
        """
        https://python-mysql-replication.readthedocs.io/en/stable/binlogstream.html
        :param stream: BinLogStreamReader object.
        """

        super(MySqlBinlogProcessor, self).__init__(**kwargs)
        self.stream = stream

        # To keep the tracking of the processed elements...
        self.log_file = None
        self.log_pos = None
        self.gtid = None
        self.xid = None

    def get_events(self) -> Iterator[Any]:
        for event in self.stream:
            self.logger.info(f"Received event: {event.__class__.__name__}.")
            self.log_file, self.log_pos = self.stream.log_file, self.stream.log_pos
            self.logger.info(f"File: {self.log_file}, Position: {self.log_pos}.")

            yield event
            self._update_log_pos(self.log_pos)

    def get_event_type(self, event: Any) -> EventType:
        if isinstance(event, QueryEvent):
            return EventType.DDL_STATEMENT

        elif isinstance(event, WriteRowsEvent):
            return EventType.INSERT

        elif isinstance(event, UpdateRowsEvent):
            return EventType.UPDATE

        elif isinstance(event, DeleteRowsEvent):
            return EventType.DELETE

        return EventType.GLOBAL

    def process_dml_event(self, event: Any, **kwargs) -> List[Record]:
        metadata = {
            "global_id": self.gtid,
            "transaction_id": self.xid,
            "event_timestamp": event.timestamp,
            "event_type": "",
            "service": self.service,
            "source": self.log_file,
            "position": self.log_pos,
            "primary_key": event.primary_key,
            "schema_name": event.schema,
            "table_name": event.table
        }

        if isinstance(event, WriteRowsEvent):
            metadata["event_type"] = EventType.INSERT

        if isinstance(event, DeleteRowsEvent):
            metadata["event_type"] = EventType.DELETE

        if isinstance(event, UpdateRowsEvent):
            metadata["event_type"] = EventType.UPDATE

            return [
                Record(record=row.get("after_values", {}), **metadata)
                for row in event.rows
            ]

        return [
            Record(record=row.get("values", {}), **metadata)
            for row in event.rows
        ]

    def process_event(self, event: Any, **kwargs):
        if isinstance(event, GtidEvent):
            self.gtid = event.gtid

        elif isinstance(event, XidEvent):
            self.xid = event.xid

        elif isinstance(event, RotateEvent):
            self.logger.info(f"NEXT FILE: {event.next_binlog}. POSITION: {event.position}.")
            self._update_log_file(event.next_binlog)
            self._update_log_pos(event.position)

    def _update_log_file(self, log_file_name: str):
        """ It updates the log_file name """

    def _update_log_pos(self, position: int):
        """ It updates the log_file position """
