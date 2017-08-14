PostgresInsert
==============

Inserts signal data into a postgres database/table
SSL mode options explained: https://www.postgresql.org/docs/current/static/libpq-ssl.html

Properties
----------
- **bulk_insert**: insert signals individually or insert the whole incoming list in one insert
- **commit_all**: hidden attribute that configures whether to commit valid transactions
- **creds**: username and password for the host database
- **db_name**: name of the database on the host
- **host**: hostname of the database to connect to
- **port**: postgres port on the host to connect to
- **retry_options**: configurable retry options for inserting
- **ssl_cert**: if ssl_mode is "verify-full" or "verify-ca", this is the path to the cert file used to verify the server.
- **ssl_mode**: select the SSL behavior for transferring data.
- **table_name**: name of the table on the database to execute commands on.

Inputs
------

Any list of signals, where the keys of the incoming data are column names,
and the values are the values needing to be inserted into those names.

Outputs
-------

Commands
--------
- **disconnect**: disconnect from the server
- **reconnect**: reconnect to the server

Dependencies
------------
psycopg2
