from unittest import TestCase
import logging
from flask_api import status    # HTTP Status Codes
from service import service
from service.models import Category
# from service.service import app, initialize_logging

######################################################################
#  T E S T   C A S E S
######################################################################
class TestCategoryServer(TestCase):
    """ Category Server Tests """

    def setUp(self):
        self.app = service.app.test_client()
        service.initialize_logging(logging.INFO)
        Category.init_db("test")
        service.data_reset()
        service.data_load({"category_name": "A"})
        service.data_load({"category_name": "B"})

    def test_index(self):
        """ Test the Home Page """
        resp = self.app.get('/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn(b'NYPL Project Demo', resp.data)

    def test_get_list(self):
        """ Get a list of categories """
        resp = self.app.get('/category')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(len(resp.data) > 0)

    def test_get_category_not_found(self):
        """ Get a category thats not found """
        resp = self.app.get('/category/0')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_category(self):
        """ Delete a category """
        resp = self.app.get('/category')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()[0]
        count_before_delete = self.get_category_count()
        resp = self.app.delete('/category/{}'.format(data['_id']),
                               content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        count_after_delete = self.get_category_count()
        self.assertEqual(count_after_delete, count_before_delete - 1)

    def get_category_count(self):
        """ save the current number of category """
        resp = self.app.get('/category')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        logging.debug('data = %s', data)
        return len(data)

if __name__ == '__main__':
    unittest.main()
