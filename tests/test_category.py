import os
from unittest import TestCase
from unittest.mock import MagicMock, patch
from requests import HTTPError, ConnectionError
from service.models import Category, DataValidationError, DatabaseConnectionError

VCAP_SERVICES = {
    'cloudantNoSQLDB': [
        {'credentials': {
            'username': 'admin',
            'password': 'pass',
            'host': 'localhost',
            'port': 5984,
            'url': 'http://admin:pass@localhost:5984'
            }
        }
    ]
}

VCAP_NO_SERVICES = {
    'noCloudant': []
}

BINDING_CLOUDANT = {
    'username': 'admin',
    'password': 'pass',
    'host': 'localhost',
    'port': 5984,
    'url': 'http://admin:pass@localhost:5984',
}

######################################################################
#  T E S T   C A S E S
######################################################################
class TestCategory(TestCase):
    """ Test Cases for Category """

    def setUp(self):
        """ Initialize the Cloudant database """
        Category.init_db("test")
        Category.remove_all()

    def test_create_a_category(self):
        """ Create a category and assert that it exists """
        category = Category(category_name='AAA')
        self.assertNotEqual(category, None)
        self.assertEqual(category.category_name, "AAA")

    def test_find_by_category_name(self):
        """ Find category by category_name"""
        Category(category_name='AAA').save()
        category = Category.find_by_category_name("AAA")
        self.assertEqual(len(category), 1)

    def test_serialize_a_category(self):
        """ Test serialization of a category """
        category = Category(category_name='AAA')
        data = category.serialize()
        self.assertNotEqual(category, None)
        self.assertEqual(data['category_name'], "AAA")

    def test_deserialize_a_category(self):
        """ Test deserialization of a category """
        data = {"category_name": "AAA"}
        category = Category()
        category.deserialize(data)
        self.assertNotEqual(category, None)
        self.assertEqual(category.category_name, "AAA")

    def test_find_a_category(self):
        """ Find a category by id """
        category = Category(category_name='AAA')
        category.save()
        new_category = Category.find(category.id)
        self.assertEqual(new_category.category_name, "AAA")

    def test_disconnect(self):
        """ Test Disconnet """
        Category.disconnect()
        category = Category("CCC")
        self.assertRaises(AttributeError, category.save)
