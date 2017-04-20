PostgresInsert
==============

Inserts signal data into a postgres database/table

Properties
--------------
-  host(str): hostname of the database to connect to
-  port(int): postgres port on the host to connect to
-  db_name(str): name of the database on the host
-  creds(object): username and password for the host database
-  table_name(str): name of the table on the database to execute commands on.
-  commit_all(bool): hidden attribute that configures whether to commit valid transactions
-  bulk_insert(bool): insert signals individually or insert the whole incoming list in one insert
-  ssl_mode(select): select the SSL behavior for transferring data.
-  ssl_cert(file): if ssl_mode is "verify-full" or "verify-ca", this is the path to the cert file used to verify the server.


SSL mode options explained:
https://www.postgresql.org/docs/current/static/libpq-ssl.html

Dependencies
----------------
psycopg2

Commands
----------------
-  connected: True if current connection succeeded and is active
-  disconnect: tear down current connection
-  reconnect: reconnect to host specified in config

Input
-------
Any list of signals, where the keys of the incoming data are column names,
and the values are the values needing to be inserted into those names.

Output
---------
None
