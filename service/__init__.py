import os
import sys
from flask import Flask

# Create Flask application
app = Flask(__name__)

# Import the rutes After the Flask app is created
from service import service, models

# Set up logging for production
service.initialize_logging()

app.logger.info(70 * '*')
app.logger.info(' NYPL SERVICE RUNNING '.center(70, '*'))
app.logger.info(70 * '*')

app.logger.info('Service initialized!')
