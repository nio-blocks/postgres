from nio.properties import BoolProperty
from nio.util.discovery import discoverable
from .postgres_base_block import PostgresBase


@discoverable
class PostgresInsert(PostgresBase):
    """A block for inserting incoming signals into a postgres database.

    Properties:

    """

    upsert = BoolProperty(title="Update conflicting keys", default=True)

    def __init__(self):
        super().__init__()

    def process_signals(self, signals):
        """execute an insert command for all incoming signals"""
        for signal in signals:
            self.execute_insert(signal.to_dict())
        # only commit transactions when all have been attempted
        if self.commit_all():
            self._commit_transactions()

    def execute_insert(self, data):
        """execute an insert query for the given data"""
        self.logger.debug('executing INSERT on data: {}'.format(data))
        try:
            self._cur.execute(self._build_insert_query_string(data),
                              tuple(data.values()))
        except:
            self.logger.exception("Could not execute command".format())
            self._rollback_transactions()

    def _build_insert_query_string(self, data):
        """build an INSERT SQL query based on the incoming (dictionary)
        data.
        """
        query_base = 'INSERT INTO {} ({}) VALUES ({})'
        # TODO: possible sql injection on db name and data keys?
        query_final = query_base.format(self.table_name(),
                                        ', '.join(list(data.keys())),
                                        ', '.join(['%s' for i in range(len(data.keys()))]))

        self.logger.debug('built query string: {}'.format(query_final))
        return query_final

    def _rollback_transactions(self):
        """rollback any pending transactions, for use in undoing erroneous
        commands
        """
        self._conn.rollback()

    def _commit_transactions(self):
        """commit any successfully executed transactions, making the changes
        permanent in the table
        """
        self._conn.commit()
