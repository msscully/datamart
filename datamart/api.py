import flask.ext.restless
from flask import request
from datamart import app, db, models
 
RESULTS_PER_PAGE = 20
MAX_RESULTS_PER_PAGE = 300
manager = flask.ext.restless.APIManager(app, flask_sqlalchemy_db=db)
 
manager.create_api(models.Dimension, 
    methods=['GET', 'POST', 'DELETE', 'PUT'], results_per_page=RESULTS_PER_PAGE)
manager.create_api(models.Variable, 
    methods=['GET', 'POST', 'DELETE', 'PUT'], results_per_page=RESULTS_PER_PAGE)
#manager.create_api(models.Facts, 
#    methods=['GET', 'POST', 'DELETE', 'PUT'], results_per_page=RESULTS_PER_PAGE)
manager.create_api(models.Role, 
    methods=['GET', 'POST', 'DELETE', 'PUT'], results_per_page=RESULTS_PER_PAGE)

def compute_results_per_page():
    """Helper function which returns the number of results per page based
    on the request argument ``results_per_page`` and the server
    configuration parameters :attr:`results_per_page` and
    :attr:`max_results_per_page`.
 
    """
    try:
        results_per_page = int(request.args.get('results_per_page'))
    except:
        results_per_page = RESULTS_PER_PAGE
    if results_per_page <= 0:
        results_per_page = RESULTS_PER_PAGE
    return min(results_per_page, MAX_RESULTS_PER_PAGE)
