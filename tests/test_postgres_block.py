from unittest.mock import patch, MagicMock
from nio.signal.base import Signal
from nio.testing.block_test_case import NIOBlockTestCase
from psycopg2._psycopg import InterfaceError

from ..postgres_insert_block import PostgresInsert
from psycopg2.extensions import cursor


class TestInsertBlock(NIOBlockTestCase):

    @patch.object(PostgresInsert, "connect")
    def test_query_building(self, patched_conn):
        """Signals pass through block unmodified."""
        blk = PostgresInsert()
        blk._conn = MagicMock()
        blk._cur = MagicMock()
        self.configure_block(blk, {'host': '127.0.0.1',
                                   'port': 5432,
                                   'db_name': 'dbname',
                                   'table_name': 'tablename',
                                   'log_level': 'DEBUG'
                                   })

        # mogrify always returns a bytestring
        blk._cur.mogrify.side_effect = [b'("testval")']
        query = blk._build_insert_query_string({"testattr": "testval"})
        self.assertEqual(query,
                         'INSERT INTO tablename (testattr) VALUES ("testval")')

        # test bulk query building
        blk._cur.mogrify.side_effect = [b'("testval"),("testval")']
        query = blk._build_insert_query_string([{"testattr": "testval"},
                                                {"testattr": "testval"}])
        self.assertEqual(query,
            'INSERT INTO tablename (testattr) VALUES ("testval"),("testval")')

        self.assert_num_signals_notified(0)
        self.assertTrue(patched_conn.called)

    @patch.object(PostgresInsert, "connect")
    def test_validation_table_name(self, patched_conn):
        blk = PostgresInsert()
        blk._conn = MagicMock()
        blk._cur = MagicMock()

        config = {'host': '127.0.0.1',
                  'port': 5432,
                  'db_name': 'dbname',
                  'table_name': '',
                  'log_level': 'DEBUG'
                  }

        # test table name validation
        for name in ['1test2', ');-- testname', 'testname;', '"testname"',
                     'test$name', 'test:name::']:
            config['table_name'] = name
            self.assertRaises(ValueError, self.configure_block, blk, config)

    @patch.object(PostgresInsert, "connect")
    def test_validation_data_keys(self, patched_conn):
        blk = PostgresInsert()
        blk._conn = MagicMock()
        blk._cur = MagicMock()
        self.configure_block(blk, {'host': '127.0.0.1',
                                   'port': 5432,
                                   'db_name': 'dbname',
                                   'table_name': 'tablename',
                                   'log_level': 'DEBUG'
                                   })

        # data key validation
        for key in ['1test2', ');-- testname', 'testname;', '"testname"',
                    'test$name', 'test:name::']:
            self.assertRaises(ValueError, blk.execute_insert, {key: "testval"})

    @patch.object(PostgresInsert, "_commit_transactions")
    @patch.object(PostgresInsert, "_rollback_transactions")
    @patch.object(PostgresInsert, "connect")
    def test_rollback_invalid_signals(self, patched_conn, patched_rollback,
                                      patched_commit):
        blk = PostgresInsert()
        blk._conn = MagicMock()
        blk._cur = MagicMock()
        self.configure_block(blk, {'host': '127.0.0.1',
                                   'port': 5432,
                                   'db_name': 'dbname',
                                   'table_name': 'tablename',
                                   'log_level': 'DEBUG'
                                   })

        blk.start()

        # block should rollback when receiving an invalid key and not commit
        # anything
        blk.process_signals([Signal({'invalid_key);': 1})])
        self.assertTrue(patched_rollback.called)
        self.assertFalse(patched_commit.called)

        blk.stop()

    @patch.object(PostgresInsert, "_commit_transactions")
    @patch.object(PostgresInsert, "_rollback_transactions")
    @patch.object(PostgresInsert, "connect")
    def test_commit_valid_signals(self, patched_conn, patched_rollback,
                                  patched_commit):
        blk = PostgresInsert()
        blk._conn = MagicMock()
        blk._cur = MagicMock()
        self.configure_block(blk, {'host': '127.0.0.1',
                                   'port': 5432,
                                   'db_name': 'dbname',
                                   'table_name': 'tablename',
                                   'log_level': 'DEBUG'
                                   })

        blk.start()

        # block should not rollback when receiving a valid key and commit the
        # transaction
        blk.process_signals([Signal({'valid_key': 1})])
        self.assertFalse(patched_rollback.called)
        self.assertTrue(patched_commit.called)

        blk.stop()

    @patch.object(PostgresInsert, "_commit_transactions")
    @patch.object(PostgresInsert, "connect")
    def test_specify_not_commit(self, patched_conn, patched_commit):
        blk = PostgresInsert()
        blk._conn = MagicMock()
        blk._cur = MagicMock()
        self.configure_block(blk, {'host': '127.0.0.1',
                                   'port': 5432,
                                   'db_name': 'dbname',
                                   'table_name': 'tablename',
                                   'log_level': 'DEBUG',
                                   'commit_all': False
                                   })

        blk.start()

        # block should commit for every signal it inserts when commit_all is
        # false
        blk.process_signals([Signal({'valid_key': 1}),
                             Signal({'valid_key': 2})])
        self.assertEqual(patched_commit.call_count, 2)

        blk.stop()

    @patch("blocks.postgres.postgres_base_block.connect")
    def test_retry_on_closed_connection(self, patched_conn):
        blk = PostgresInsert()

        self.configure_block(blk, {'host': '127.0.0.1',
                                   'port': 5432,
                                   'db_name': 'dbname',
                                   'table_name': 'tablename',
                                   'log_level': 'DEBUG',
                                   'bulk_insert': True,
                                   "retry_options": {"max_retry": 1,
                                                     "multiplier": 0.005}
                                   })
        blk._cur.mogrify.side_effect = [b'("testval1")', b'("testval2")']

        blk.start()
        # process one signal, this should go through successfully and not
        # have to reconnect
        blk.process_signals([Signal({'valid_key': 1})])
        self.assertEqual(patched_conn.call_count, 1)
        self.assertEqual(blk._conn.commit.call_count, 1)

        # now the connection has been closed, the block should retry the commit
        # once which will call connect once more, for a total of two.
        blk._conn.commit.side_effect = [InterfaceError, True]
        blk.process_signals([Signal({'valid_key': 2})])
        self.assertEqual(patched_conn.call_count, 2)
        # +1 from the previous signal
        self.assertEqual(blk._conn.commit.call_count, 3)
