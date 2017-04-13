import re
from psycopg2 import connect

from nio.block.base import Block
from nio.command import command
from nio.block.mixins import LimitLock, Retry
from nio.properties import (VersionProperty, StringProperty, IntProperty,
                            BoolProperty, PropertyHolder, ObjectProperty)
from nio.util.discovery import not_discoverable


class AuthCreds(PropertyHolder):
    username = StringProperty(title="Username", default="", allow_none=True)
    password = StringProperty(title="Password", default="", allow_none=True)


@not_discoverable
@command('connected', method='connected')
@command('reconnect', method='connect')
@command('disconnect', method='disconnect')
class PostgresBase(LimitLock, Retry,  Block):
    """A block for communicating with an postgres database.

    Properties:
        host(str): hostname of the database to connect to
        port(int): postgres port on the host to connect to
        db_name(str): name of the database on the host
        creds(object): username and password for the host database
        table_name(str): name of the table on the database to execute commands
                         on.
        commit_all(bool): hidden attribute that configures whether to commit
                          valid transactions
    """

    version = VersionProperty('1.0.0')
    host = StringProperty(title="Host",
                          default="[[POSTGRES_HOST]]")
    port = IntProperty(title="Port",
                       default="[[POSTGRES_PORT]]")
    db_name = StringProperty(title="DB Name", allow_none=False)
    creds = ObjectProperty(AuthCreds, title="Credentials", default=AuthCreds())
    table_name = StringProperty(title="Table Name", allow_none=False)
    commit_all = BoolProperty(title="Commit transactions", default=True,
                              visible=False)

    def __init__(self):
        super().__init__()
        self._conn = None
        self._cur = None

    def configure(self, context):
        super().configure(context)

        # validate any user-given variables
        self._validate_string(self.table_name())

        self.connect()

    def stop(self):
        self.logger.debug('closing postgres connection...')
        self.disconnect()
        super().stop()

    def process_signals(self, signals):
        self.execute_with_lock(
            self._locked_process_signals, 100, signals=signals)

    def _locked_process_signals(self, signals):
        pass

    def connected(self):
        return self._conn.status

    def connect(self):
        """connect to the database and create the cursor object for executing
        commands
        """
        self.logger.debug('Connecting to postgres db...')
        self._conn = connect(database=self.db_name(),
                             user=self.creds().username(),
                             password=self.creds().password(),
                             host=self.host(),
                             port=self.port())
        self._cur = self._conn.cursor()

    def disconnect(self):
        """disconnect from the database and close the cursor object"""
        self._cur.close()
        self._conn.close()

    @staticmethod
    def _validate_string(string):
        """validate any string going into an SQL statement to protect
        against SQL injection. Every valid SQL identifier and keyword must
        obey the format represented by the regex below. If the variable is
        found to be invalid, this fails configuration of this block."""

        if not re.match("^[a-zA-Z_][a-zA-Z0-9_]*$", string):
            raise ValueError("SQL keyword or identifier '{}' did not pass "
                             "validation.".format(string))
