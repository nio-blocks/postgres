from .postgres_base_block import PostgresBase


class PostgresInsert(PostgresBase):
    """A block for inserting incoming signals into a postgres database.

    Properties:

    """

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
        data. psycopg2 automatically escapes/sanitizes values passed into
        execute and mogrify. First mogrifying the table name and data keys
        assures escaping of those variables, and the data values will be
        escaped when execute is called.
        """
        query_base = 'INSERT INTO %s (%s) VALUES (%s)'
        query_final = self._cur.mogrify(query_base, [self.table_name(),
                                                     ', '.join(list(data.keys())),
                                                     ', '.join(['%s'] * len(data))
                                                     ])

        # get rid of quotations
        query_final = query_final.replace(b"'", b'')

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
