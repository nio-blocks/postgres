from nio.block.base import Block
from nio.command import command
from nio.util.discovery import not_discoverable
from nio.properties import VersionProperty, StringProperty, IntProperty
from psycopg2 import connect


@command('Connection status', method='connection_status')
@not_discoverable
class PostgresBase(Block):
    """A block for communicating with an postgres database.

    Properties:
        host:
        port:

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
        self._conn = connect(database=self.db_name(), user=self.user_name(),
                             password=self.password(), host=self.host(),
                             port=self.port())
        self._cur = self._conn.cursor()

    def stop(self):
        self.logger.debug('closing postgres connection...')
        self._cur.close()
        self._conn.close()
        super().stop()

    def connection_status(self):
        return 'Connected' if self._conn.status else 'Not connected'
