from unittest.mock import patch, MagicMock
from nio.signal.base import Signal
from nio.testing.block_test_case import NIOBlockTestCase
from ..postgres_insert_block import PostgresInsert
import psycopg2


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
        blk.start()
        blk.process_signals([Signal({"testattr": "testval"})])
        blk.stop()

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
