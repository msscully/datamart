import flask.ext.restless
from datamart import app, db, models
 
manager = flask.ext.restless.APIManager(app, flask_sqlalchemy_db=db)
 
manager.create_api(models.Dimension, 
    methods=['GET', 'POST', 'DELETE', 'PUT'], results_per_page=20)
manager.create_api(models.Variable, 
    methods=['GET', 'POST', 'DELETE', 'PUT'], results_per_page=20)
