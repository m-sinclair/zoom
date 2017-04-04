"""
    test_store.py

    Test the store module
"""

from decimal import Decimal
from datetime import date, time, datetime
import unittest

from zoom.store import Entity, EntityStore
from zoom.database import setup_test


class Person(Entity):
    pass


class TestPerson(Entity):
    pass


class TestStore(unittest.TestCase):

    def setUp(self):
        self.db = setup_test()
        self.db.autocommit(1)
        self.people = EntityStore(self.db, Person)
        self.joe_id = self.people.put(Person(name='Joe', age=50))
        self.sam_id = self.people.put(Person(name='Sam', age=25))
        self.people.put(Person(name='Ann', age=30))
        self.id_name = '_id'

    def tearDown(self):
        self.people.zap()
        self.db.close()

    def test_put(self):
        jane_id = self.people.put(Person(name='Jane', age=25))
        person = self.people.get(jane_id)
        del person['__store']
        self.assertEqual(dict(person), dict(_id=jane_id, name='Jane', age=25))

    def test_get(self):
        joe = self.people.get(self.joe_id)
        del joe['__store']
        self.assertEqual(dict(joe), dict(_id=self.joe_id, name='Joe', age=50))

    def test_get_missing(self):
        joe = Person(name='Joe', age=50)
        joe_id = self.people.put(joe)
        person = self.people.get(joe_id)
        self.assertEqual(None, self.people.get(joe_id + 1))

    def test_get_multiple(self):
        def sort_order(item):
            return keys.index(item['_id'])
        keys = [self.sam_id, self.joe_id]
        r = self.people.get(keys)
        sam = self.people.get(self.sam_id)
        joe = self.people.get(self.joe_id)
        self.assertEqual(sorted(r, key=sort_order), [sam, joe])

    def test_get_put_get(self):
        sam = self.people.get(self.sam_id)
        self.assertEqual(sam.age, 25)
        self.assertEqual(len(self.people), 3)
        sam.age += 1
        self.people.put(sam)
        self.assertEqual(len(self.people), 3)
        person = self.people.get(self.sam_id)
        self.assertEqual(person.age, 26)

    def test_get_save(self):
        sam = self.people.get(self.sam_id)
        self.assertEqual(sam.age, 25)
        self.assertEqual(len(self.people), 3)
        sam.age += 1
        sam.save()
        self.assertEqual(len(self.people), 3)
        person = self.people.get(self.sam_id)
        self.assertEqual(person.age, 26)

    def test_resave(self):
        jane = Person(name='Jane', age=25)
        jane_id = self.people.put(jane)
        self.assertEqual(jane[self.id_name], 4)
        jane['age'] += 1
        jane.age += 1
        new_id = jane.save()
        self.assertEqual(new_id, 4)
        person = self.people.get(jane_id)
        self.assertEqual(person.age, 27)

    def test_delete_by_entity(self):
        sam = self.people.get(self.sam_id)
        self.assert_(sam)
        self.people.delete(sam)
        sam = self.people.get(self.sam_id)
        self.assertEqual(None, sam)

    def test_delete_by_id(self):
        sam = self.people.get(self.sam_id)
        self.assert_(sam)
        self.people.delete(self.sam_id)
        sam = self.people.get(self.sam_id)
        self.assertEqual(None, sam)

    def test_none(self):
        al_id = self.people.put(Person(name='Al', age=None))
        al = self.people.get(al_id)
        self.assertEqual(al.age, None)

    def test_bool(self):
        al_id = self.people.put(Person(name='Al', done=False))
        al = self.people.get(al_id)
        self.assertEqual(al.done, False)
        al.done = True
        self.people.put(al)
        person = self.people.get(al_id)
        self.assertEqual(person.done, True)

    def test_kind(self):
        self.assertEqual(self.people.kind, 'person')
        self.assertEqual(EntityStore(self.db, TestPerson).kind, 'test_person')

    def test_len(self):
        self.assertEqual(3, len(self.people))

    def test_zap(self):
        self.assertEqual(3, len(self.people))
        self.people.zap()
        self.assertEqual(0, len(self.people))
