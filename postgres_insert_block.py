from nio.properties import BoolProperty
from psycopg2._psycopg import Error as Psycopg2Error

from .postgres_base_block import PostgresBase
from collections import OrderedDict


class PostgresInsert(PostgresBase):
    """A block for inserting incoming signals into a postgres database.

    Properties:
        bulk_insert(bool): if this is set to True, then inserts will be
        performed in bulk, instead of inserting each signal individually.
    """

    bulk_insert = BoolProperty(title="Bulk Insert Incoming Signals",
                               default=False)

    def _locked_process_signals(self, signals):
        """execute an insert command for all incoming signals"""

        # bulk inserting is not affected by commit_all, as it can only be
        # one insertion per list of signals, therefore only one commit
        if self.bulk_insert():
            try:
                self.execute_insert([OrderedDict(signal.to_dict()) for signal
                                     in signals])
                self._commit_transactions()
            except:
                self.logger.exception("Could not execute bulk insert query")
                self._rollback_transactions()
        else:
            # insert individual signals
            if self.commit_all():
                # commit only after every insert has been completed
                try:
                    for signal in signals:
                        self.execute_insert(OrderedDict(signal.to_dict()))
                    self._commit_transactions()
                except:
                    self.logger.exception("One or more insert queries could "
                                          "not be executed")
                    self._rollback_transactions()
            else:
                # commit after every insert
                try:
                    for signal in signals:
                        self.execute_insert(OrderedDict(signal.to_dict()))
                        self._commit_transactions()
                except:
                    self.logger.exception("Insert query could not be executed")
                    self._rollback_transactions()

    def execute_insert(self, data):
        """execute an insert query for the given data"""
        self.logger.debug('executing INSERT on data: {}'.format(data))

        # first check to see if the keys are valid
        if self.bulk_insert():
            # grab the keys of the first signal
            for key in data[0].keys():
                self._validate_string(key)
                self._validate_column_name(key)
        else:
            for key in data.keys():
                self._validate_string(key)
                self._validate_column_name(key)

        # execute the insert query. the query string is built with the data
        # already in it, so jsut execute that query here.
        self._cur.execute(self._build_insert_query_string(data))
        if self._conn.notices:
            self.logger.warning("Database returned the following notices: {}"
                                .format(self._conn.notices))

    def _build_insert_query_string(self, data):
        """build an INSERT SQL query based on the incoming data. the keys are
        validated before building this query, so just insert those into the
        query. Then build the value tuple(s), which are mogrified/escaped
        correctly while building the string.
        """

        if isinstance(data, list):
            # this is a bulk insert. Take the keys from the first signal and
            # assume that those keys will be the same for all the insert
            # signals, since we're only inserting into one table. Then make
            # n tuples of values where n is the number of signals.
            keys_tuple = ', '.join(list(data[0].keys()))
            value_tuple = ','.join(
                self._cur.mogrify(
                    "({})".format(','.join(["%s"] * len(data_dict))),
                    tuple(data_dict.values())).decode()
                for data_dict in data)
        elif isinstance(data, dict):
            # single insert
            keys_tuple = ', '.join(list(data.keys()))
            value_tuple = self._cur.mogrify(
                "({})".format(','.join(["%s"] * len(data))),
                tuple(data.values())
            ).decode()
        else:
            raise TypeError("Could not build a query string with data "
                            "of type {}. Expecting dict or list."
                            .format(type(data)))

        query_base = 'INSERT INTO {} ({}) VALUES {}'
        query_final = query_base.format(self.table_name(),
                                        keys_tuple,
                                        value_tuple)

        self.logger.debug('built query string: {}'.format(query_final))

        return query_final

    def _rollback_transactions(self):
        """rollback any pending transactions, for use in undoing erroneous
        queries. No changes will be made to the table.
        """
        try:
            self.execute_with_retry(self._conn.rollback)
        except Psycopg2Error:
            self.logger.exception("Could not execute rollback")

    def _commit_transactions(self):
        """commit any successfully executed transactions, making the changes
        permanent in the table
        """
        try:
            self.execute_with_retry(self._conn.commit)
        except Psycopg2Error:
            self.logger.exception("Could not execute commit")

    def before_retry(self, *args, **kwargs):
        # when the new connection is made here the old one is torn down and
        # loses the transaction information for the current transaction. This
        # means the data will not be inserted for this transaction.
        self.logger.warning("reconnecting to DB before retry, this will "
                            "forfeit the current transaction")
        self.connect()

    def _validate_column_name(self, key):
        # make sure user input column name is exactly equal to one of the
        # column names queried in PostgresBase.configure()

        if key not in self.column_names:
            raise ValueError("{} is not a valid column in the {} table."
                             .format(key, self.table_name))
