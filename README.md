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

Dependencies
----------------
psycopg2

Commands
----------------
-  connection_status: True if current connection succeeded and is active
-  disconnect: tear down current connection
-  reconnect: reconnect to host specified in config

Input
-------
Any list of signals, where the keys of the incoming data are column names,
and the values are the values needing to be inserted into those names.

Output
---------
None
