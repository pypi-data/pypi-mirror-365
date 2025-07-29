# -*- coding: utf-8 -*-

from typing import Any, List, Iterator, Dict

from pymongo.change_stream import ChangeStream

from core_cdc.base import Record, EventType
from .base import IProcessor


class MongoDbStreamProcessor(IProcessor):
    """
    It processes the events from the MongoDB Stream.

    A change stream is a real-time stream of database changes that flows from your
    database to your application. With change streams, your applications can react—in real
    time—to data changes in a single collection, a database, or even an entire
    deployment. For apps that rely on notifications of changing data, change
    streams are critical.

    More information:
    https://www.mongodb.com/basics/change-streams
    """

    def __init__(self, stream: ChangeStream, save_full_event: bool = True, **kwargs):
        """
        :param stream: DatabaseChangeStream object.
        :param save_full_event: If True, all the event will be streamed, otherwise only fullDocument.

        To create a stream you can use:
            * db.collection.watch()
            * db.watch()

        Example:
            pipeline = [{'$match': {'operationType': 'insert'}}, {'$match': {'operationType': 'replace'}}]
            MongoDbStreamProcessor(
                stream = MongoClient(...)["database"].<collection>.watch(pipeline)
            )

        More information...
            * https://www.mongodb.com/basics/change-streams
            * https://www.mongodb.com/docs/manual/changeStreams/#open-a-change-stream
            * https://www.mongodb.com/docs/manual/reference/method/db.watch/#db.watch--
        """

        super(MongoDbStreamProcessor, self).__init__(**kwargs)
        self.save_full_event = save_full_event
        self.stream = stream

    def get_events(self) -> Iterator[Any]:
        for event in self.stream:
            self.logger.info(
                f"Received event: {event.get('operationType')} "
                f"for document: {event.get('documentKey', {}).get('_id')}."
            )

            event["clusterTime"] = event["clusterTime"].time if event.get("clusterTime") else None
            yield event

            # To store the token to resume execution...
            self.save_resume_token(event["_id"])

    def get_event_type(self, event: Dict) -> EventType:
        opt_type = event.get("operationType")
        if opt_type == "insert":
            return EventType.INSERT

        elif opt_type in ("replace", "update"):
            return EventType.UPDATE

        elif opt_type == "delete":
            return EventType.DELETE

        return EventType.GLOBAL

    def process_dml_event(self, event: Any, **kwargs) -> List[Record]:
        metadata = {
            "global_id": None,
            "transaction_id": None,
            "event_timestamp": event["clusterTime"],
            "event_type": self.get_event_type(event),
            "service": self.service,
            "source": None,
            "position": 0,
            "primary_key": "_id",
            "schema_name": event["ns"]["db"],
            "table_name": event["ns"]["coll"]
        }

        event["documentKey"]["_id"] = str(event["documentKey"]["_id"])
        if event.get("fullDocument"):
            event["fullDocument"]["_id"] = str(event["fullDocument"]["_id"])

        return [
            Record(
                record=event if self.save_full_event else event.get("fullDocument", {}),
                **metadata
            )
        ]

    def save_resume_token(self, token):
        """
        It stores the token that can be used to resume the
        process in a certain point...
        """
