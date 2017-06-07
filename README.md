PostgresInsert
==============

Inserts signal data into a postgres database/table

SSL mode options explained: https://www.postgresql.org/docs/current/static/libpq-ssl.html

Properties
--------------
-  host(type:str): hostname of the database to connect to
-  port(type:int): postgres port on the host to connect to
-  db_name(type:str): name of the database on the host
-  creds(type:object): username and password for the host database
-  table_name(type:str): name of the table on the database to execute commands on.
-  commit_all(type:bool): hidden attribute that configures whether to commit valid transactions
-  bulk_insert(type:bool): insert signals individually or insert the whole incoming list in one insert
-  ssl_mode(type:select): select the SSL behavior for transferring data.
-  ssl_cert(type:file): if ssl_mode is "verify-full" or "verify-ca", this is the path to the cert file used to verify the server.



Dependencies
----------------
psycopg2

Commands
----------------
-  disconnect: tear down current connection
-  reconnect: reconnect to host specified in config

Input
-------
Any list of signals, where the keys of the incoming data are column names,
and the values are the values needing to be inserted into those names.

Output
---------
None
