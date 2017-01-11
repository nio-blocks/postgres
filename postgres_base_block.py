from nio.block.base import Block
from nio.command import command
from nio.util.discovery import not_discoverable
from nio.properties import (VersionProperty, StringProperty, IntProperty,
                            BoolProperty, PropertyHolder, ObjectProperty)
from psycopg2 import connect


class AuthCreds(PropertyHolder):
    username = StringProperty(title="Username", default="", allow_none=True)
    password = StringProperty(title="Password", default="", allow_none=True)


@not_discoverable
@command('Connection status', method='connection_status')
@command('Reconnect', method='connect')
@command('Disconnect', method='disconnect')
class PostgresBase(Block):
    """A block for communicating with an postgres database.

    Properties:
        host(str): hostname of the database to connect to
        port(int): postgres port on the host to connect to
        db_name(str): name of the database on the host
        creds(object): username and password for the host database
        password(str): password credential of the postgres server
        table_name(str): name of the table on the database to execute commands
                         on.
    """

    version = VersionProperty('1.0.0')
    host = StringProperty(title="Host",
                          default="[[POSTGRES_HOST]]")
    port = IntProperty(title="Port",
                       default="[[POSTGRES_PORT]]")
    db_name = StringProperty(title="DB Name", allow_none=False)
    creds = ObjectProperty(AuthCreds, title="Credentials", default=AuthCreds())
    table_name = StringProperty(title="Table name", allow_none=False)
    commit_all = BoolProperty(title="Commit transactions", default=True,
                              visible=False)

    def __init__(self):
        super().__init__()
        self._conn = None
        self._cur = None

    def configure(self, context):
        super().configure(context)
        self.connect()

    def stop(self):
        self.logger.debug('closing postgres connection...')
        self.disconnect()
        super().stop()

    def connection_status(self):
        return 'Connected' if self._conn.status else 'Not connected'

    def connect(self):
        """connect to the database and create the cursor object for executing
        commands
        """
        self.logger.debug('Connecting to postgres db...')
        try:
            self._conn = connect(database=self.db_name(),
                                 user=self.creds().username(),
                                 password=self.creds().password(),
                                 host=self.host(),
                                 port=self.port())
            self._cur = self._conn.cursor()
        except:
            # fail to start the service if a connection can't be made
            raise

    def disconnect(self):
        """disconnect from the database and close the cursor object"""
        self._cur.close()
        self._conn.close()
