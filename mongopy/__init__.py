
class MongoPy(object):
    """ Memory Storage (for now)

    Public Methods:
    insert
    update
    upsert
    delete
    find
    find_one
    ensure_index
    """
    _ID_KEY = '_id'
    _ID_BITS = 64

    def __init__(self):
        self._queue = []
        self._indexes = {}

        self.ensure_index(self._ID_KEY) # create an index for _ID_KEY

    # public:

    def insert(self, item):
        if not isinstance(item, dict): raise TypeError('Must be a dict')

        if item.has_key(self._ID_KEY):
            if self.find_one({self._ID_KEY:item[self._ID_KEY]}):
                raise ValueError('Cannot create a document with existing id')
        else:
            self._assign_id(item)

        self._queue.append(item)
        self._create_index_for(item)

        return item[self._ID_KEY]

    def upsert(self, item):
        """ repair this """
        if item.has_key(self._ID_KEY):
            doc = self.find_one({self._ID_KEY:item[self._ID_KEY]})
            if doc:
                # basically delete it to be replaced... ughh
                self.delete({self._ID_KEY:item[self._ID_KEY]})
        else:
            # document has no id, so we're not updating
            # assign one to insert
            self._assign_id(item)

        self.insert(item)

    def update(self, query, updates):
        if not isinstance(query, dict): raise TypeError('Query type: dict')
        if not isinstance(updates, dict): raise TypeError('Updates type: dict')

        self.KEYWORDS = {
            '$push': self._push_value_onto_key,
            '$pop': self._pop_index_from_key,
            '$inc': self._increment_value_of_key,
            '$dec': self._decrement_value_of_key,
            '$set': self._set_value_of_key,
            '$unset': self._unset_key,
            }

        docs = self.find(query)
        if not docs: return # no documents matched the query

        for doc in docs:
            self._update_doc(doc, updates)


    def delete(self, query):
        # take advantages of indexes
        matches = self.find(query)
        deleted = len(matches)

        for doc in matches:
            self._remove_index_for(doc)
            self._queue.pop(self._queue.index(doc))

        return deleted

    def find(self, query=None):
        # no query specified, return all items?
        # this should return an iterator or a cursor obj
        if not query: return self._queue

        #needs so much more optimization
        if not isinstance(query, dict): raise TypeError('Query must be a dict')

        indexed = []
        index_exists = False

        compare_keys = zip(self._indexes.keys(), query.keys())
        key_matches = [qk for ik, qk in compare_keys if ik == qk]

        if key_matches:
            key = key_matches[0] # if one index matches, only need one...
            index_exists = True
            indexed.append(self._indexes[key].get(query[key], None))

        return self._search_queue_or_indexed(query, indexed, index_exists=True)

    def find_one(self, query):
        results = self.find(query)
        return results[0] if results else None

    def ensure_index(self, key):
        if key not in self._indexes:
            self._create_index_for_key(key)

        return True if self._indexes.has_key(key) else False

    # private:

    def _assign_id(self, item):
        item[self._ID_KEY] = self._generate_id()

    def _generate_id(self):
        """ simple for now """
        import random
        return unicode(random.getrandbits(self._ID_BITS))

    def _search_queue_or_indexed(self, query, indexed, index_exists=True):
        search = indexed if index_exists else self._queue
        found = [doc for doc in self._queue if self._kv_compare(query, doc)]
        return found

    def _kv_compare(self, query, doc):
        match = 1
        for key in query.keys():
            if not doc.has_key(key):
                match = 0
                break
            elif query[key] != doc[key]:
                match = 0
                break

        return True if match else False

    def _remove_index_for(self, item):
        for key in item:
            if key in self._indexes:
                self._indexes[key].pop(item.get(key))

    def _create_index_for(self, item):
        # unique indexes only for now
        for key in self._indexes:
            if item.has_key(key):
                self._indexes[key][item.get(key)] = item

    def _create_index_for_key(self, key):
        # unique indexes only for now
        if not self._indexes.has_key(key):
            self._indexes[key] = {}

            for item in self._queue:
                if item.has_key(key):
                    self._indexes[key][item.get(key)] = item

    def _update_doc(self, orig_doc, update_doc):
        #doc_idx = self._queue.index(doc)
        #doc = self._queue[doc_idx] # is this redundant?

        for key in update_doc.keys():
            # root level for now, recursion to support all to come..
            if isinstance(update_doc[key], dict):
                self._update_doc_dict_value(orig_doc, key, update_doc[key])
            else:
                orig_doc[key] = update_doc[key]

        self._create_index_for(orig_doc) # update all indexes with new values

    def _update_doc_dict_value(self, doc, key, d_value):
        if len(d_value.keys()) > 1:
            # no keywords specificed at root level
            doc[key] = d_value
            return

        # operations will have only one key
        # i.e. {'count': {'$inc': 1}}
        d_key = d_value.keys()[0]
        kw_func = self.KEYWORDS.get(d_key, None)
        if kw_func:
            kw_func(doc, key, d_value[d_key])
        else:
            doc[key] = d_value

    def _pop_index_from_key(self, doc, key, value):
        doc[key].pop(value)

    def _push_value_onto_key(self, doc, key, value):
        # supports top-level only for now
        doc[key].append(value)

    def _increment_value_of_key(self, doc, key, value):
        doc[key] += value

    def _decrement_value_of_key(self, doc, key, value):
        doc[key] -= value

    def _set_value_of_key(self, doc, key, value):
        doc[key] = value

    def _unset_key(self, doc, key, value):
        if value == 1:
            doc.pop(key)

