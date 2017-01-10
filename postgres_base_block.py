from nio.block.base import Block
from nio.command import command
from nio.util.discovery import not_discoverable
from nio.properties import VersionProperty, StringProperty, IntProperty
from psycopg2 import connect


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
        user_name(str): user name credential of the postgres server
        password(str): password credential of the postgres server
    """

    version = VersionProperty('1.0.0')
    host = StringProperty(title="Host",
                          default="[[POSTGRES_HOST]]")
    port = IntProperty(title="Port",
                       default="[[POSTGRES_PORT]]")
    db_name = StringProperty(title="DB Name", allow_none=False)
    user_name = StringProperty(title="User Name", default="test")
    password = StringProperty(title="Password", allow_none=False)

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
            self._conn = connect(database=self.db_name(), user=self.user_name(),
                                 password=self.password(), host=self.host(),
                                 port=self.port())
            self._cur = self._conn.cursor()
        except:
            # fail to start the service if a connection can't be made
            raise

    def disconnect(self):
        """disconnect from the database and close the cursor object"""
        self._cur.close()
        self._conn.close()