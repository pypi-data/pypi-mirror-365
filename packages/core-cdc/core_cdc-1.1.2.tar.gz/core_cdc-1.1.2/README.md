# core-cdc (CDC a.k.a Change Data Capture)
_______________________________________________________________________________

It provides the core mechanism and required resources to 
implement "Change Data Capture" services...


## Execution Environment

### Install libraries
```shell
pip install --upgrade pip 
pip install virtualenv
```

### Create the Python Virtual Environment.
```shell
virtualenv --python={{python-version}} .venv
virtualenv --python=python3.11 .venv
```

### Activate the Virtual Environment.
```shell
source .venv/bin/activate
```

### Install required libraries.
```shell
pip install .
```

### Optional libraries.
```shell
pip install '.[all]'  # For all...
pip install '.[mysql]'
pip install '.[mongo]'
pip install '.[snowflake]'
```

### Check tests and coverage.
```shell
python manager.py run-tests
python manager.py run-coverage
```


## Engines

### MySQL

Let's create a MySql server using Docker...
```shell
docker run \
  --name=MySqlServer \
  --env=MYSQL_ROOT_PASSWORD=mysql_password \
  --volume=/var/lib/mysql \
  -p 3306:3306 \
  --restart=no \
  --runtime=runc \
  -d mysql:5.7
```

While using library `core-cdc>=1.0.2` that uses `mysql-replication>=1.0.7` the 
value of variable `binlog_row_metadata` must be `FULL`.

#### Check the value in the server...
```commandline
SHOW VARIABLES LIKE 'binlog_row_metadata'
```

#### Update the MySQL configuration file...
This file is usually named my.cnf on Unix/Linux systems 
and my.ini on Windows. The location of this file can vary depending 
on your operating system and MySQL installation method. Common 
locations include `/etc/mysql/my.cnf`, `/etc/my.cnf`, 
or `/usr/local/mysql/my.cnf`.

Add or modify the binlog_row_metadata option in the [mysqld] section 
of the configuration file. Set it to FULL to enable 
full metadata logging.
```text
[mysqld]
binlog_row_metadata = FULL
```

If you are using Docker based on `oraclelinux-slim` you can use:
```shell
docker exec -it {container-name} bash
microdnf install nano
nano /etc/my.cnf
```

Then, the below example script showcase how to process
the MySQL BinLog...
```python
# -*- coding: utf-8 -*-

import logging
import os
from pprint import pprint
from typing import Any
from typing import List

from core_mixins.logger import get_logger
from pymysqlreplication import BinLogStreamReader

from core_cdc.base import Record
from core_cdc.processors.mysql_binlog import MySqlBinlogProcessor
from core_cdc.targets.base import Target

cxn_params = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "passwd": "mysql_password"
}

logger = get_logger(
    log_level=int(os.getenv("LOGGER_LEVEL", str(logging.INFO))),
    reset_handlers=True)


class CustomMySqlBinlogProcessor(MySqlBinlogProcessor):
    """ Custom class to implement required methods """

    @classmethod
    def registered_name(cls) -> str:
        return cls.__name__

    def process_dml_event(self, event: Any, **kwargs) -> List[Record]:
        recs = super().process_dml_event(event, **kwargs)
        logger.info("The following records will be processed...")

        for rec in recs:
            pprint(rec.to_json())

        return recs


class CustomTarget(Target):
    @classmethod
    def registered_name(cls) -> str:
        return cls.__name__

    def _save(self, records: List[Record], **kwargs):
        logger.info(f"Saving: {records}")


try:
    target = CustomTarget(
        logger=logger, execute_ddl=True,
        send_data=True)

    stream = BinLogStreamReader(
        resume_stream=False,
        connection_settings=cxn_params,
        blocking=True,
        freeze_schema=False,
        server_id=1)

    processor = CustomMySqlBinlogProcessor(
        stream=stream,
        targets=[target],
        service=os.getenv("SERVICE_NAME", "Functional-Tests"),
        logger=logger)

    processor.execute()

except Exception as error:
    logger.error(f"An error has been raised. Error: {error}.")
```

You will see something like...
```text
[INFO] connection_settings: {'host': 'localhost', 'port': 3306, 'user': 'root', 'passwd': 'mysql_password', 'charset': 'utf8'}
[INFO] blocking: True
[INFO] allowed_events_in_packet: frozenset({<class 'pymysqlreplication.event.GtidEvent'>, <class 'pymysqlreplication.event.RandEvent'>, <class 'pymysqlreplication.event.StopEvent'>, <class 'pymysqlreplication.event.MariadbGtidListEvent'>, <class 'pymysqlreplication.event.QueryEvent'>, <class 'pymysqlreplication.row_event.TableMapEvent'>, <class 'pymysqlreplication.row_event.UpdateRowsEvent'>, <class 'pymysqlreplication.event.FormatDescriptionEvent'>, <class 'pymysqlreplication.row_event.WriteRowsEvent'>, <class 'pymysqlreplication.row_event.DeleteRowsEvent'>, <class 'pymysqlreplication.event.MariadbAnnotateRowsEvent'>, <class 'pymysqlreplication.event.ExecuteLoadQueryEvent'>, <class 'pymysqlreplication.event.MariadbStartEncryptionEvent'>, <class 'pymysqlreplication.event.HeartbeatLogEvent'>, <class 'pymysqlreplication.event.XAPrepareEvent'>, <class 'pymysqlreplication.event.MariadbGtidEvent'>, <class 'pymysqlreplication.event.MariadbBinLogCheckPointEvent'>, <class 'pymysqlreplication.event.BeginLoadQueryEvent'>, <class 'pymysqlreplication.event.UserVarEvent'>, <class 'pymysqlreplication.event.XidEvent'>, <class 'pymysqlreplication.row_event.PartialUpdateRowsEvent'>, <class 'pymysqlreplication.event.RowsQueryLogEvent'>, <class 'pymysqlreplication.event.RotateEvent'>, <class 'pymysqlreplication.event.PreviousGtidsEvent'>})
[INFO] server_id: 1
[INFO] Reading events from the stream...
[WARNING] 
                    Before using MARIADB 10.5.0 and MYSQL 8.0.14 versions,
                    use python-mysql-replication version Before 1.0 version 
[INFO] Received event: RotateEvent.
[INFO] File: c8db74e52957-bin.000002, Position: 4.
[INFO] NEXT FILE: c8db74e52957-bin.000002. POSITION: 4.
[INFO] Received event: FormatDescriptionEvent.
[INFO] File: c8db74e52957-bin.000002, Position: 123.
[INFO] Received event: PreviousGtidsEvent.
[INFO] File: c8db74e52957-bin.000002, Position: 154.
```

Let's execute some DDL and DML statements and follow the 
output in the console...

#### Create database
```shell
CREATE DATABASE IF NOT EXISTS test_database;
```

```text
[INFO] Received event: QueryEvent.
[INFO] File: c8db74e52957-bin.000002, Position: 418.
[INFO] The below query was executed in: CustomTarget.
[INFO] /* ApplicationName=DBeaver 24.3.0 - SQLEditor <Script-4.sql> */ CREATE DATABASE IF NOT EXISTS test_database
```

#### Create table
```shell
CREATE TABLE person (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100),
    birth_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

```text
[INFO] Received event: QueryEvent.
[INFO] File: c8db74e52957-bin.000002, Position: 872.
[INFO] The below query was executed in: CustomTarget.
[INFO] /* ApplicationName=DBeaver 24.3.0 - SQLEditor <Script-4.sql> */ CREATE TABLE person (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100),
    birth_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

```

#### Inserting records
```shell
INSERT INTO person (first_name, last_name, email, birth_date)
VALUES
('John', 'Doe', 'john.doe@example.com', '1990-01-15'),
('Jane', 'Smith', 'jane.smith@example.com', '1985-07-22');
```

```text
[INFO] Received event: QueryEvent.
[INFO] File: c8db74e52957-bin.000002, Position: 1018.
[INFO] Received event: TableMapEvent.
[INFO] File: c8db74e52957-bin.000002, Position: 1088.
[INFO] Received event: WriteRowsEvent.
[INFO] File: c8db74e52957-bin.000002, Position: 1211.
[INFO] The following records will be processed...
{'event_timestamp': 1733197735,
 'event_type': 'INSERT',
 'global_id': None,
 'position': 1211,
 'primary_key': '',
 'record': {'UNKNOWN_COL0': 1,
            'UNKNOWN_COL1': 'John',
            'UNKNOWN_COL2': 'Doe',
            'UNKNOWN_COL3': 'john.doe@example.com',
            'UNKNOWN_COL4': '1990-01-15',
            'UNKNOWN_COL5': '2024-12-03T03:48:55'},
 'schema_name': 'test_database',
 'service': 'Functional-Tests',
 'source': 'c8db74e52957-bin.000002',
 'table_name': 'person',
 'transaction_id': None}
{'event_timestamp': 1733197735,
 'event_type': 'INSERT',
 'global_id': None,
 'position': 1211,
 'primary_key': '',
 'record': {'UNKNOWN_COL0': 2,
            'UNKNOWN_COL1': 'Jane',
            'UNKNOWN_COL2': 'Smith',
            'UNKNOWN_COL3': 'jane.smith@example.com',
            'UNKNOWN_COL4': '1985-07-22',
            'UNKNOWN_COL5': '2024-12-03T03:48:55'},
 'schema_name': 'test_database',
 'service': 'Functional-Tests',
 'source': 'c8db74e52957-bin.000002',
 'table_name': 'person',
 'transaction_id': None}
[INFO] Saving: [<core_cdc.base.Record object at 0x7281f3b55340>, <core_cdc.base.Record object at 0x7281f3b55370>]
[INFO] 2 records were sent to: CustomTarget!
[INFO] {'target': 'CustomTarget', 'number_of_records': 2, 'event_type': <EventType.INSERT: 'INSERT'>, 'schema': 'test_database', 'table': 'person'}
[INFO] Received event: XidEvent.
[INFO] File: c8db74e52957-bin.000002, Position: 1242.
```

#### Updating a record
```shell
UPDATE person
SET first_name = 'Jonathan', last_name = 'Dover'
WHERE id = 1;
```

### MongoDB

First, let's create a local cluster to test the example, for it,
let's use Docker...
```shell
docker network create mongoCluster
docker run -d --rm -p 27017:27017 --name mongo1 --network mongoCluster mongo:5 mongod --replSet myReplicaSet --bind_ip localhost,mongo1
docker run -d --rm -p 27018:27017 --name mongo2 --network mongoCluster mongo:5 mongod --replSet myReplicaSet --bind_ip localhost,mongo2
docker run -d --rm -p 27019:27017 --name mongo3 --network mongoCluster mongo:5 mongod --replSet myReplicaSet --bind_ip localhost,mongo3

docker exec -it mongo1 mongosh --eval "rs.initiate({                                                                                                                                                         ─╯
 _id: \"myReplicaSet\",
 members: [
   {_id: 0, host: \"mongo1\"},
   {_id: 1, host: \"mongo2\"},
   {_id: 2, host: \"mongo3\"}
 ]
})"
```

Check the cluster status...
```shell
docker ps
docker exec -it mongo1 mongosh --eval "rs.status()" 
```

Below, an example of how to use and process MongoDB Change Streams
using this library...
```python
# -*- coding: utf-8 -*-

import contextlib
import json
import logging
import os
from typing import List, Any, Dict
from pprint import pprint

from core_db.engines.mongo import MongoClient
from core_mixins.logger import get_logger
from pymongo.errors import PyMongoError

from core_cdc.base import Record
from core_cdc.processors.mongo_stream import MongoDbStreamProcessor
from core_cdc.targets.base import Target

token_path = "./local_token.txt"

logger = get_logger(
    logger_name="MongoDbStreamProcessorTestCases",
    log_level=int(os.getenv("LOGGER_LEVEL", str(logging.INFO))),
    reset_handlers=True)


class CustomMongoDbStreamProcessor(MongoDbStreamProcessor):
    """ Custom class to implement required methods """

    @classmethod
    def registered_name(cls) -> str:
        return cls.__name__

    def process_dml_event(self, event: Any, **kwargs) -> List[Record]:
        recs = super().process_dml_event(event, **kwargs)
        logger.info("The following records will be processed...")

        for rec in recs:
            pprint(rec.to_json())

        return recs

    def save_resume_token(self, token: Dict):
        with open(token_path, mode="w+") as file_:
            file_.write(json.dumps(token))


class CustomTarget(Target):
    @classmethod
    def registered_name(cls) -> str:
        return cls.__name__

    def _save(self, records: List[Record], **kwargs):
        logger.info(f"Saving: {records}")

client = MongoClient(
    host="localhost", port=27017, database="test",
    username=None, password=None,
    directConnection=True)

target = CustomTarget(
    logger=logger, execute_ddl=True,
    send_data=True)

with contextlib.suppress(Exception):
    with open(token_path) as file:
        resume_token = json.loads(file.read())

try:
    logger.info("Connecting to MongoDB server...")
    client.connect()

    with client.cxn.watch(full_document="updateLookup") as stream:
        processor = CustomMongoDbStreamProcessor(
            stream=stream,
            targets=[target],
            service=os.getenv("SERVICE_NAME", "Functional-Tests"),
            logger=logger)

        processor.execute()

except PyMongoError as error:
    logger.error(f"An error has been raised. Error: {error}.")
```

Once the  above script is executed...
```text
[INFO] Connecting to MongoDB server...
[INFO] Reading events from the stream...
```

Then, we can add a record via:
```shell
mongosh "mongodb://localhost:27017/"
use test
db.createCollection("people")
db.getCollection("people").insert({"name": "Alek", "age": 39})
```

The output...
```text
[INFO] Received event: insert for document: 674d3c4778be6ac4a6210f24.
[INFO] The following records will be processed...
{'event_timestamp': 1733114951,
 'event_type': 'INSERT',
 'global_id': None,
 'position': 0,
 'primary_key': '_id',
 'record': {'_id': {'_data': '82674D3C47000000012B022C0100296E5A1004EED3A947B256417181A8398FEE8F22CD46645F69640064674D3C4778BE6AC4A6210F240004'},
            'clusterTime': 1733114951,
            'documentKey': {'_id': '674d3c4778be6ac4a6210f24'},
            'fullDocument': {'_id': '674d3c4778be6ac4a6210f24',
                             'age': 39,
                             'name': 'Alek'},
            'ns': {'coll': 'people', 'db': 'test'},
            'operationType': 'insert'},
 'schema_name': 'test',
 'service': 'Functional-Tests',
 'source': None,
 'table_name': 'people',
 'transaction_id': None}
[INFO] Saving: [<core_cdc.base.Record object at 0x7ab441c21910>]
[INFO] 1 records were sent to: CustomTarget!
[INFO] {'target': 'CustomTarget', 'number_of_records': 1, 'event_type': <EventType.INSERT: 'INSERT'>, 'schema': 'test', 'table': 'people'}
```

Let's update the record, like: 
`db.getCollection("people").updateOne({"name": "Alek"}, { "$set": {"age": 30}})`,
the output will be...
```text
[INFO] Received event: update for document: 674d3c4778be6ac4a6210f24.
[INFO] The following records will be processed...
{'event_timestamp': 1733115348,
 'event_type': 'UPDATE',
 'global_id': None,
 'position': 0,
 'primary_key': '_id',
 'record': {'_id': {'_data': '82674D3DD4000000012B022C0100296E5A1004EED3A947B256417181A8398FEE8F22CD46645F69640064674D3C4778BE6AC4A6210F240004'},
            'clusterTime': 1733115348,
            'documentKey': {'_id': '674d3c4778be6ac4a6210f24'},
            'fullDocument': {'_id': '674d3c4778be6ac4a6210f24',
                             'age': 30,
                             'name': 'Alek'},
            'ns': {'coll': 'people', 'db': 'test'},
            'operationType': 'update',
            'updateDescription': {'removedFields': [],
                                  'truncatedArrays': [],
                                  'updatedFields': {'age': 30}}},
 'schema_name': 'test',
 'service': 'Functional-Tests',
 'source': None,
 'table_name': 'people',
 'transaction_id': None}
[INFO] Saving: [<core_cdc.base.Record object at 0x7ab441e88ec0>]
[INFO] 1 records were sent to: CustomTarget!
[INFO] {'target': 'CustomTarget', 'number_of_records': 1, 'event_type': <EventType.UPDATE: 'UPDATE'>, 'schema': 'test', 'table': 'people'}
```

Let's delete it using:
`db.getCollection("people").remove({"name": "Alek"})`, the
console will show...
```text
[INFO] Received event: delete for document: 674d3c4778be6ac4a6210f24.
[INFO] The following records will be processed...
{'event_timestamp': 1733115451,
 'event_type': 'DELETE',
 'global_id': None,
 'position': 0,
 'primary_key': '_id',
 'record': {'_id': {'_data': '82674D3E3B000000012B022C0100296E5A1004EED3A947B256417181A8398FEE8F22CD46645F69640064674D3C4778BE6AC4A6210F240004'},
            'clusterTime': 1733115451,
            'documentKey': {'_id': '674d3c4778be6ac4a6210f24'},
            'ns': {'coll': 'people', 'db': 'test'},
            'operationType': 'delete'},
 'schema_name': 'test',
 'service': 'Functional-Tests',
 'source': None,
 'table_name': 'people',
 'transaction_id': None}
[INFO] Saving: [<core_cdc.base.Record object at 0x7ab441e89130>]
[INFO] 1 records were sent to: CustomTarget!
[INFO] {'target': 'CustomTarget', 'number_of_records': 1, 'event_type': <EventType.DELETE: 'DELETE'>, 'schema': 'test', 'table': 'people'}
```

Delete the Docker's containers...
```shell
docker stop mongo1 mongo2 mongo3
```
