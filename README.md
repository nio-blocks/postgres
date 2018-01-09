PostgresInsert
==============
The PostgresInsert block inserts incoming signal data into a postgres database/table.  
SSL mode options explained: https://www.postgresql.org/docs/current/static/libpq-ssl.html

Properties
----------
- **bulk_insert**: If `False` (unchecked), the block will insert each incoming signal individually. If `True`, the block will insert the whole incoming list in one insert.
- **commit_all**: Hidden attribute, defaults to `True`. When `True`, block will commit all valid transactions.
- **creds**: Username and password for the host database.
- **db_name**: Name of the database on the host.
- **host**: Host address of the database to connect to.
- **port**: Postgres port on the host to connect to.
- **retry_options**: A selection of options to choose from when retrying to make a connection.
- **ssl_cert**: If **SSL option** is 'verify-full' or 'verify-ca', this is the path to the cert file used to verify the server.
- **ssl_mode**: The type of SSL behavior for verifying the exchange of data between the service and Postgres database.
- **table_name**: Name of the table on the database to execute commands on.

Inputs
------
- **default**: Any list of signals, where the keys of the incoming data are column names, and the values are the values needing to be inserted into those names.

Outputs
-------
None

Commands
--------
- **disconnect**: Disconnect from the server Postgres is hosted on.
- **reconnect**: reconnect to the server Postgres is hosted on.

Dependencies
------------
psycopg2

