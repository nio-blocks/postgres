from nio.util.discovery import discoverable
from .postgres_base_block import PostgresBase


@discoverable
class PostgresInsert(PostgresBase):
    """A block for inserting incoming signals into a postgres database.

    Properties:

    """

    def __init__(self):
        super().__init__()

    def configure(self, context):
        super().configure(context)

    def process_signals(self, signals):
        # execute an insert command for incoming signals
        for signal in signals:
            self.execute_insert(signal.to_dict())

    def execute_insert(self, data):
        # execute an insert query for the given data
        self.logger.debug('executing INSERT on data: {}'.format(data))
        self._cur.execute(self._build_insert_query_string(data))

    def _build_insert_query_string(self, data):
        # build an SQL query based on the incoming (dictionary) data
        query_base = 'INSERT INTO {} ({}) VALUES {}' \
                     .format(self.db_name(),
                             ', '.join(list(data.keys())),
                             list(data.values()))

        self.logger.debug('built query string: {}'.format(query_base))
        return query_base
