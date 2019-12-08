import os
import json
import logging
import pandas as pd
from retry import retry
from cloudant.client import Cloudant
from cloudant.query import Query
from cloudant.adapters import Replay429Adapter
from requests import HTTPError, ConnectionError

# get configruation from enviuronment (12-factor)
ADMIN_PARTY = os.environ.get('ADMIN_PARTY', 'False').lower() == 'true'
CLOUDANT_HOST = os.environ.get('CLOUDANT_HOST', 'localhost')
CLOUDANT_USERNAME = os.environ.get('CLOUDANT_USERNAME', 'admin')
CLOUDANT_PASSWORD = os.environ.get('CLOUDANT_PASSWORD', 'pass')

# global variables for retry (must be int)
RETRY_COUNT = int(os.environ.get('RETRY_COUNT', 10))
RETRY_DELAY = int(os.environ.get('RETRY_DELAY', 1))
RETRY_BACKOFF = int(os.environ.get('RETRY_BACKOFF', 2))

class DatabaseConnectionError(Exception):
    """ Custom Exception when database connection fails """
    pass

class DataValidationError(Exception):
    """ Used for a data validation errors when deserializing """
    pass

class Category():
    """
    Class that represents a category
    """
    logger = logging.getLogger('flask.app')
    client = None   # cloudant.client.Cloudant
    database = None # cloudant.database.CloudantDatabase

    def __init__(self, category_name=None):
        self.id = None
        self.category_name = category_name

    @retry(HTTPError, delay=RETRY_DELAY, backoff=RETRY_BACKOFF,
           tries=RETRY_COUNT, logger=logger)
    def create(self):
        """
        Creates a new category in the database
        """
        if self.category_name is None:
            raise DataValidationError('category_name is not set')
        try:
            Category.logger.info("Create a new category_name")
            category = self.find_by_category_name(self.category_name)
            print(category)
            if len(category) != 0:
                raise DataValidationError('category_name : '+ self.category_name + ' already exist')

            document = self.database.create_document(self.serialize())
        except HTTPError as err:
            Category.logger.warning('Create failed: %s', err)
            return
        if document.exists():
            self.id = document['_id']

    @retry(HTTPError, delay=RETRY_DELAY, backoff=RETRY_BACKOFF,
           tries=RETRY_COUNT, logger=logger)
    def update(self):
        """ Updates a Category in the database """
        if self.id:
            Category.logger.info("Update a category: {%s}", self.id)
            try:
                document = self.database[self.id]
            except KeyError:
                document = None
            if document:
                document.update(self.serialize())
                document.save()

    @retry(HTTPError, delay=RETRY_DELAY, backoff=RETRY_BACKOFF,
           tries=RETRY_COUNT, logger=logger)
    def save(self):
        """
        Saves a Category to DB
        """
        if self.id:
            self.update()
        else:
            self.create()

    def serialize(self):
        """ Serializes a Category into a dictionary """
        category = {
            "category_name": self.category_name
        }
        if self.id:
            category['_id'] = self.id
        return category

    def deserialize(self, data):
        """
        Deserializes a Category from a dictionary
        Args:
            data (dict): A dictionary containing the Category data
        """
        try:
            self.category_name = data['category_name']
            if not isinstance(self.category_name, str):
                raise TypeError('category_name required string')
        except KeyError as error:
            raise DataValidationError('Invalid Category: missing '
                                      + error.args[0])
        except TypeError as error:
            raise DataValidationError('Invalid Category: body of ' \
                                      'request contained ' \
                                      'bad or no data : ' \
                                      + error.args[0])
        # if there is no id and the data has one, assign it
        if not self.id and '_id' in data:
            self.id = data['_id']

        return self

    @retry(HTTPError, delay=RETRY_DELAY, backoff=RETRY_BACKOFF,
           tries=RETRY_COUNT, logger=logger)
    def delete(self):
        """ Deletes a Category from the database """
        if self.id:
            try:
                document = self.database[self.id]
            except KeyError:
                document = None
            if document:
                document.delete()

######################################################################
#  S T A T I C   D A T A B S E   M E T H O D S
######################################################################
    @classmethod
    def connect(cls,adapter=Replay429Adapter(retries=10, initialBackoff=0.01)):
        """ Connect to the server """
        cls.client.connect()

    @classmethod
    def disconnect(cls):
        """ Disconnect from the server """
        cls.client.disconnect()

    @classmethod
    def remove_all(cls):
        """ Removes all documents from the database (use for testing)  """
        for document in cls.database:
            document.delete()

    @classmethod
    def drop(cls, dbname):
        """ drop the database (use for testing)  """
        Category.client.delete_database(dbname)

    @classmethod
    def all(cls):
        """ Query that returns all Category """
        results = []
        for doc in cls.database:
            category = Category().deserialize(doc)
            category.id = doc['_id']
            results.append(category)
        return results

######################################################################
#  F I N D E R   M E T H O D S
######################################################################

    @classmethod
    def find(cls, id):
        """ Find a Category by id """
        cls.logger.info('Processing lookup for id %s ...', id)
        try:
            document = cls.database[id]
            return Category().deserialize(document)
        except KeyError:
            return None

    @classmethod
    @retry(HTTPError, delay=RETRY_DELAY, backoff=RETRY_BACKOFF,
           tries=RETRY_COUNT, logger=logger)
    def find_by(cls, **kwargs):
        """ Find records using selector """
        query = Query(cls.database, selector=kwargs)
        results = []
        for doc in query.result:
            category = Category()
            category.deserialize(doc)
            results.append(category)
        return results


    @classmethod
    @retry(HTTPError, delay=RETRY_DELAY, backoff=RETRY_BACKOFF,
           tries=RETRY_COUNT, logger=logger)
    def find_by_category_name(cls, category_name):
        """ Find a Category by category_name
            Args:
            category_name (string): the category_name of the Category you
            want to match
        """
        return cls.find_by(category_name=category_name)

############################################################
#  C L O U D A N T   D A T A B A S E   C O N N E C T I O N
############################################################
    @staticmethod
    def init_db(dbname="categories"):
        """
        Initialized Coundant database connection
        """
        opts = {}
        # Try and get VCAP from the environment
        if 'VCAP_SERVICES' in os.environ:
            Category.logger.info('Found Cloud Foundry VCAP_SERVICES bindings')
            vcap_services = json.loads(os.environ['VCAP_SERVICES'])
            # Look for Cloudant in VCAP_SERVICES
            for service in vcap_services:
                if service.startswith('cloudantNoSQLDB'):
                    opts = vcap_services[service][0]['credentials']

        # if VCAP_SERVICES isn't found, maybe we are running on Kubernetes?
        if not opts and 'BINDING_CLOUDANT' in os.environ:
            Category.logger.info('Found Kubernetes BINDING_CLOUDANT bindings')
            opts = json.loads(os.environ['BINDING_CLOUDANT'])

        # If Cloudant not found in VCAP_SERVICES or BINDING_CLOUDANT
        # get it from the CLOUDANT_xxx environment variables
        if not opts:
            Category.logger.info('VCAP_SERVICES and BINDING_CLOUDANT undefined.')
            opts = {
                "username": CLOUDANT_USERNAME,
                "password": CLOUDANT_PASSWORD,
                "host": CLOUDANT_HOST,
                "port": 5984,
                "url": "http://"+CLOUDANT_HOST+":5984/"
            }

        if any(k not in opts for k in ('host', 'username',
                                       'password', 'port', 'url')):
            raise DatabaseConnectionError('Error - Failed \
                                          to retrieve options. ' \
                                          'Check that app is bound to \
                                          a Cloudant service.')

        Category.logger.info('Cloudant Endpoint: %s', opts['url'])
        try:
            if ADMIN_PARTY:
                Category.logger.info('Running in Admin Party Mode...')
            Category.client = Cloudant(
                opts['username'],
                opts['password'],
                url=opts['url'],
                connect=True,
                auto_renew=True,
                admin_party=ADMIN_PARTY,
                adapter=Replay429Adapter(retries=10, initialBackoff=0.1)
            )
        except ConnectionError:
            raise DatabaseConnectionError('Cloudant service \
                                           could not be reached')

        # Create database if it doesn't exist
        try:
            print(dbname)
            Category.database = Category.client[dbname]
        except KeyError:
            # Create a database using an initialized client
            Category.database = Category.client.create_database(dbname)
        # check for success
        if not Category.database.exists():
            raise DatabaseConnectionError('Database [{}] could not \
                                          be obtained'.format(dbname))
