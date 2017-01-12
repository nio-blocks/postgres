from .postgres_base_block import PostgresBase


class PostgresInsert(PostgresBase):
    """A block for inserting incoming signals into a postgres database."""

    def __init__(self):
        super().__init__()

    def process_signals(self, signals):
        """execute an insert command for all incoming signals"""

        # if commits are needed, commit after succesfully executing all
        # queries, else rollback all transactions if any of them do not work.
        if self.commit_all():
            try:
                for signal in signals:
                    self.execute_insert(signal.to_dict())
                self._commit_transactions()
            except:
                self.logger.exception("Could not execute insert query")
                self._rollback_transactions()
        else:
            for signal in signals:
                try:
                    self.execute_insert(signal.to_dict())
                except:
                    self.logger.exception("Could not execute insert query")

    def execute_insert(self, data):
        """execute an insert query for the given data"""
        self.logger.debug('executing INSERT on data: {}'.format(data))

        # first check to see if the keys are valid
        for key in data.keys():
            self._validate_string(key)

        self._cur.execute(self._build_insert_query_string(data),
                          tuple(data.values()))

    def _build_insert_query_string(self, data):
        """build an INSERT SQL query based on the incoming (dictionary)
        data. psycopg2 automatically escapes/sanitizes values passed into
        execute and mogrify. First mogrifying the table name and data keys
        assures escaping of those variables, and the data values will be
        escaped when execute is called.
        """

        query_base = 'INSERT INTO {} ({}) VALUES ({})'
        query_final = query_base.format(self.table_name(),
                                        ', '.join(list(data.keys())),
                                        ', '.join(['%s'] * len(data))
                                        )

        # get rid of quotations
        query_final = query_final.replace("'", '')

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
