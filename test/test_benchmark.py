import time
import sys, os.path
sys.path.insert(0,os.path.join(os.path.dirname(__file__),'..'))

from unittest import TestCase

from mongopy import MongoPy


class BenchmarkTestCases(TestCase):

    RECORDS = 1000

    def _data_records(self):
        self.one_data = ['val'+str(i)*100 for i in range(self.RECORDS)]
        self.two_data = ['val'+str(i)*1000 for i in range(self.RECORDS)]

        for i, v in enumerate(self.one_data):
            self.db.insert({'one':v, 'two': self.two_data[i]})

    def setUp(self):
        super(BenchmarkTestCases, self).setUp()
        self.db = MongoPy()
        self.db.ensure_index('one')
        self._data_records()

    def test_find(self):
        start = time.time()
        for v in self.one_data:
            res = self.db.find_one({'one': v})
        elapsed = time.time() - start
        print "Found %d records in %.2f seconds" % (self.RECORDS, elapsed)

    def test_ensure_index(self):
        start = time.time()
        for v in self.one_data:
            res = self.db.ensure_index('two')
            assert res
        elapsed = time.time() - start
        print "Ensured index of %d records in %.2f seconds" % (
            self.RECORDS, elapsed)



