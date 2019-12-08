import sys
import logging
from flask import jsonify, request, url_for, make_response, abort, render_template
from flask_api import status    # HTTP Status Codes
from flask_restplus import Api, Resource, fields, reqparse, inputs
from service.models import Category, DataValidationError
from service.train import SimilarityModel
# Import Flask application
from . import app

######################################################################
# GET INDEX
######################################################################
@app.route('/')
def index():
    """ Root URL response """
    return render_template('page.html')

@app.route('/search', methods = ['POST', 'GET'])
def search():
    if request.method == 'POST' and request.form['target_word'] is not None:
        target_word = request.form['target_word']
        res = SimilarityModel.top_k_similarity(target_word, 5)
        return render_template('results.html', result=res, len=len(res))
    else:
        return render_template('page.html')

api = Api(app,
          version='1.0.0',
          title='NYPL REST API Service',
          description='This is a NYPL server.',
          default='category',
          default_label='categories operations',
          doc='/apidocs/index.html',
         )

app.config['RESTPLUS_MASK_SWAGGER'] = False

category_model = api.model('Category', {
    '_id': fields.String(readOnly=True,
                         description='The unique id assigned \
                         internally by service'),
    'category_name': fields.String(required=True,
                              description='The name of the category')
})

create_model = api.model('Category', {
    'category_name': fields.String(required=True,
                              description='The name of the category')
})

# query string arguments
category_args = reqparse.RequestParser()
category_args.add_argument('target_word', type=str,
                            required=False, location='args', \
                            help='search related categories')
category_args.add_argument('number', type=int,
                            required=False, location='args', \
                            help='top n, default 5')

######################################################################
# Error Handlers
######################################################################
@api.errorhandler(DataValidationError)
def request_validation_error(error):
    """ Handles Value Errors from bad data """
    message = str(error)
    app.logger.error(message)
    return {
        'status_code': status.HTTP_400_BAD_REQUEST,
        'error': 'Bad Request',
        'message': message
    }, status.HTTP_400_BAD_REQUEST


######################################################################
#  PATH: /category/{id}
######################################################################
@api.route('/category/<id>')
@api.param('id', 'The Category identifier')
class CategoryResource(Resource):
    """
    CategoryResource class
    Allows the manipulation of a single category
    GET /category/{id} - Returns a category with the id
    DELETE /category/{id} -  Deletes a category with the id
    """
    #------------------------------------------------------------------
    # RETRIEVE A CATEGORY
    #------------------------------------------------------------------
    @api.doc('get_category')
    @api.response(404, 'Category not found')
    @api.marshal_with(category_model)
    def get(self, id):
        """
        Retrieve a single category
        This endpoint will return a category based on it's id
        """
        app.logger.info('Request for category with id: %s', id)
        category = Category.find(id)
        if not category:
            api.abort(status.HTTP_404_NOT_FOUND,
                      "Category with id '{}' was not \
                      found.".format(id))
        return category.serialize(), status.HTTP_200_OK
    #------------------------------------------------------------------
    # DELETE A CATEGORY
    #------------------------------------------------------------------
    @api.doc('delete_category')
    @api.response(204, 'Category deleted')
    def delete(self, id):
        """
        Delete a category
        This endpoint will delete a category based on the id specified
        in the path
        """
        app.logger.info('Request to delete category with id: %s', id)
        category = Category.find(id)
        if category:
            category.delete()
        return '', status.HTTP_204_NO_CONTENT

######################################################################
# PATH: /category
######################################################################
@api.route('/category', strict_slashes=False)
class CategoryCollection(Resource):
    """ Handles all interactions with collections of categories """
    #------------------------------------------------------------------
    # ADD A NEW CATEGORY
    #------------------------------------------------------------------
    @api.doc('create_category')
    @api.expect(create_model)
    @api.response(400, 'The posted data was not valid')
    @api.response(201, 'Category created successfully')
    @api.marshal_with(category_model, code=201)
    def post(self):
        """
        Creates a Category
        This endpoint will create a Category based
        the data in the body that is posted
        """
        app.logger.info('Request to create a category')
        check_content_type('application/json')
        category = Category()
        app.logger.debug('Payload = %s', api.payload)
        category.deserialize(api.payload)
        category.save()
        location_url = api.url_for(CategoryResource,
                                   id=category.id, _external=True)
        return category.serialize(), status.HTTP_201_CREATED, \
        {'Location': location_url}

    #------------------------------------------------------------------
    # LIST ALL CATEGORIES
    #------------------------------------------------------------------
    # GET request to /category?target_word={target_word}&number={number}
    @api.doc('list_categories')
    @api.expect(category_args, validate=True)
    @api.marshal_list_with(category_model)
    def get(self):
        """ Returns all of the categories """
        app.logger.info('Request for categories lists')
        categories = []
        args = category_args.parse_args()
        target_word = args['target_word']
        number = args['number']
        if target_word is not None:
            if number is not None:
                res = SimilarityModel.top_k_similarity(target_word, number)
            else:
                res = SimilarityModel.top_k_similarity(target_word, 5)
            for word in res:
                categories.append(Category(category_name=word))
        else:
            categories = Category.all()
        results = [e.serialize() for e in categories]
        return results, status.HTTP_200_OK

######################################################################
# PATH: /category/reset
######################################################################
@app.route('/category/reset', methods=['DELETE'])
def category_reset():
    """ Removes all categories """
    Category.remove_all()
    return make_response('', status.HTTP_200_OK)

######################################################################
# LOAD ALL CATEGORIES IN CSV (for testing only)
######################################################################
@app.route('/category/loaddata', methods=['POST'])
def category_load():
    """ Load all categories into the database """
    load_all()
    return make_response('', status.HTTP_200_OK)

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################
# @app.before_first_request
def init_db(dbname):
    """ Initlaize the model """
    Category.init_db(dbname)

# load sample data
def data_load(payload):
    """ Loads a category into the database """
    category = Category(payload['category_name'])
    category.save()

# load all data from categories.csv
# def load_all():
#     """ Load all categories into the database """
#     categories = SimilarityModel.read_categories_csv()
#     for name in categories:
#         category = Category(category_name=name)
#         category.save()

def data_reset():
    """ Removes all categories from the database """
    Category.remove_all()

def db_drop(dbname):
    """ Removes all categories from the database """
    Category.drop(dbname)

def check_content_type(content_type):
    """ Checks that the media type is correct """
    if request.headers['Content-Type'] == content_type:
        return
    app.logger.error('Invalid Content-Type: %s',
                     request.headers['Content-Type'])
    abort(415, 'Content-Type must be {}'.format(content_type))

def initialize_logging(log_level=logging.INFO):
    """ Initialized the default logging to STDOUT """
    if not app.debug:
        # Set up default logging for submodules to use STDOUT
        # datefmt='%m/%d/%Y %I:%M:%S %p'
        fmt = '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        logging.basicConfig(stream=sys.stdout, level=log_level, format=fmt)
        # Make a new log handler that uses STDOUT
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(fmt))
        handler.setLevel(log_level)
        # Remove the Flask default handlers and use our own
        handler_list = list(app.logger.handlers)
        for log_handler in handler_list:
            app.logger.removeHandler(log_handler)
        app.logger.addHandler(handler)
        app.logger.setLevel(log_level)
        app.logger.propagate = False
        app.logger.info('Logging handler established')
