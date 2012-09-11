(mongopy)

a simple memory store for storing schemaless data (taking cues from MongoDB)

Description
-----------

Anyone even considering this package is going to already enjoy MongoDB and
the coders at 10gen.com.  I really enjoy it too, but sometimes I just need a
better storage system for quick, fast access to things I don't necessarily
want to write to disk.

That will be a typical use for this application.  Someone who wants to have a
memory solution that's quick to instantiate and has the beginnings of a
beautiful interface that is modeled after MongoDB.

Usage
-----

Instantiation:

    >>> from mongopy import MongoPy
    >>> db = MongoPy()

Inserting:

    >>> db.insert({'name': 'David', 'level': 6})
    u'8491991710235950406'
    >>> db.insert({'name': 'Goliath', 'level': 0})
    u'15400048366191294602'

Finding:

    >>> db.find()
    [{'_id': u'8491991710235950406', 'name': 'David', 'level': 6}, {'_id': u'15400048366191294602', 'name': 'Goliath', 'level': 0}]
    >>> db.find_one({'_id': '8491991710235950406'})
    {'_id': u'8491991710235950406', 'name': 'David', 'level': 6}
    >>> db.find_one({'_id': '15400048366191294602'})
    {'_id': u'15400048366191294602', 'name': 'Goliath', 'level': 0}

    >>> db.find({'level': {'$in': [0,1,2,3]}})
    [{'_id': u'15400048366191294602', 'name': 'Goliath', 'level': 0}]
    >>> db.find({'level': {'$lte': [7]}})
    [{'_id': u'8491991710235950406', 'name': 'David', 'level': 6}, {'_id': u'15400048366191294602', 'name': 'Goliath', 'level': 0}]
    >>> db.find_one({'level': {'$gt': 4}})
    {'_id': u'8491991710235950406', 'name': 'David', 'level': 6}

Updating:

    >>> db.update({'name': 'David'}, {'level': {'$inc': 1}})
    >>> db.update({'_id': u'15400048366191294602'}, {'level': {'$unset': 1}})
    >>> db.find()
    [{'_id': u'8491991710235950406', 'name': 'David', 'level': 7}, {'_id': u'15400048366191294602', 'name': 'Goliath'}]

Deleting:

    >>> db.delete({'name': 'Goliath'})
    1
    >>> db.find_one({'name': 'Goliath'})
    >>>

Basic Indexing:

    >>> db.ensure_index('name')
    True
    >>> db._indexes['name']
    {'Goliath': {'_id': u'7220570962932597029', 'name': 'Goliath', 'level': 0}, 'David': {'_id': u'12745564493724871612', 'name': 'David', 'level': 6}}

