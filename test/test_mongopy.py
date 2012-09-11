
import sys, os.path
sys.path.insert(0,os.path.join(os.path.dirname(__file__),'..'))

from unittest import TestCase

from mongopy import MongoPy


class MongoPyTestCases(TestCase):

    def _create_test_records(self):
        self._new_fixtures = [
            {'user': 'david', 'level': 7, 'authed': True, 'perms': []},
            {'user': 'saul', 'level': 2, 'authed': False, 'perms': [], 'a':5},
            {'user': 'goliath', 'level': 1, 'authed': False, 'perms': [
                'test0','test1','test2','test3']},
            ]
        self._ids = [self.store.insert(doc) for doc in self._new_fixtures]
        self._id_key = self.store._ID_KEY

    def setUp(self):
        super(MongoPyTestCases, self).setUp()
        self.store = MongoPy()
        self._create_test_records()

    def test_operation_unset(self):
        self.store.update({'user': 'david'}, {'perms': {'$unset': 1}})
        doc = self.store.find_one({'user': 'david'})
        assert 'perms' not in doc

    def test_operation_set(self):
        self.store.update({'user': 'saul'}, {'a': {'$set': 4}})
        doc = self.store.find_one({'user': 'saul'})
        assert doc['a'] == 4

    def test_operation_pop(self):
        doc = self.store.find_one({'user': 'goliath'})
        doc_id = doc[self._id_key]
        assert len(doc['perms']) == 4
        assert doc['perms'][0] == 'test0'
        assert doc['perms'][-1] == 'test3' # baseline

        self.store.update({self._id_key: doc_id}, {'perms': {'$pop': 0}})
        self.store.update({self._id_key: doc_id}, {'perms': {'$pop': 1}})
        self.store.update({self._id_key: doc_id}, {'perms': {'$pop': -1}})

        doc = self.store.find_one({'user': 'goliath'})
        assert len(doc['perms']) == 1
        assert 'test1' in doc['perms']

    def test_operation_push(self):
        doc = self.store.find_one({'user': 'david'})
        doc_id = doc[self._id_key]
        assert not doc['perms'] # baseline

        self.store.update({self._id_key: doc_id},{'perms': {'$push': 'admin'}})
        doc = self.store.find_one({'user': 'david'})
        assert 'admin' in doc['perms']

    def test_operation_increment(self):
        doc = self.store.find_one({'user': 'david'})
        doc_id = doc[self._id_key]
        assert doc['level'] == 7 # baseline

        self.store.update({self._id_key: doc_id}, {'level': {'$inc': 1}})
        doc = self.store.find_one({'user': 'david'})
        assert doc['level'] == 8

    def test_find(self):
        # one key match
        assert len(self.store.find({'authed': False})) == 2

        # multiple key match
        assert len(self.store.find({'authed': False, 'user': 'goliath'})) == 1

        # no matches
        assert len(self.store.find({'user': 'unknown'})) == 0

    def test_find_one(self):
        assert self.store.find_one({self._id_key: self._ids[0]})
        assert not self.store.find_one({self._id_key: "1"})

    def test_ensure_index(self):
        self.store.ensure_index('user')
        assert self.store._indexes.has_key('user')
        assert len(self.store._indexes['user'].keys()) > 1

    def test_delete(self):
        doc = self.store.find_one({'user': 'david'})
        assert self.store.delete({'user': 'david'}) == 1
        assert not self.store._indexes[self._id_key].has_key(doc[self._id_key])

        self.store.insert(doc)
        assert self.store.delete(doc) == 1
        assert not self.store._indexes[self._id_key].has_key(doc[self._id_key])

    def test_id_index(self):
        assert self.store._indexes.has_key(self._id_key)
        assert self.store._indexes[self._id_key].has_key(self._ids[0])
        assert self.store._indexes[self._id_key].has_key(self._ids[1])
        assert self.store._indexes[self._id_key].has_key(self._ids[2])



