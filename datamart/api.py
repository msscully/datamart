import flask.ext.restless
from flask import request, _request_ctx_stack, current_app
from datamart import app, db, models, security
import sqlalchemy
from flask.ext.restless import ProcessingException
from flask.ext.security import current_user, utils
from flask.ext.principal import Identity, identity_changed 
from flask.ext.security.decorators import BasicAuth
from sqlalchemy.orm.util import class_mapper
 
DIMENSION_DATATYPES = {
    'String': sqlalchemy.String,
    'Integer': sqlalchemy.Integer,
    'Float': sqlalchemy.Float,
    'Boolean': sqlalchemy.Boolean
}

def is_mapped_class(cls):
    try:
        class_mapper(cls)
        return True
    except:
        return False

RESULTS_PER_PAGE = 50
MAX_RESULTS_PER_PAGE = 10000
manager = flask.ext.restless.APIManager(app, flask_sqlalchemy_db=db)
 
def auth_func(**kw):
    auth = request.authorization or BasicAuth(username=None, password=None)
    user = security.datastore.find_user(email=auth.username)

    if user and utils.verify_and_update_password(auth.password, user):
        security.datastore.commit()
        app = current_app._get_current_object()
        _request_ctx_stack.top.user = user
        identity_changed.send(app,
                              identity=Identity(user.id))
        return
    if not current_user.is_authenticated():
        raise ProcessingException(message='Not authenticated!')

def auth_admin(**kw):
    auth_func(**kw)
    if not current_user.is_admin:
        raise ProcessingException(message='Permission denied!')


def facts_preproc(search_params=None, **kw):
    if search_params is not None:
        order_by = search_params.get('order_by',[])

        var_datatypes = current_user.approved_vars_and_datatypes()
        variable_ids = [str(i.id) for i in models.Variable.query.all()]

        def _fix_field(field):
            if field in var_datatypes:
                model_field = models.Facts.values[field]
                data_type = var_datatypes[field]
                return sqlalchemy.cast(model_field, DIMENSION_DATATYPES[data_type])
            else:
                raise ProcessingException('Access not authorized.')

        def _build_filters(filters):
           if "and" in filters:
               return {'and': _build_filters(filters['and'])}
           
           elif "or" in filters:
               return {'or': _build_filters(filters['or'])}
           
           elif isinstance(filters, list):
               return [_build_filters(filt) for filt in filters]
        
           elif "name" in filters or "op" in filters or "val" in filters or "field" in filters:
               if filters.get("field", False) and filters["field"] in variable_ids:
                   filters["field"] = _fix_field(filters["field"])
               if filters.get("name", False) and filters["name"] in variable_ids:
                   filters["name"] = _fix_field(filters["name"])

               return filters

        filters = _build_filters(search_params.get('filters',dict()))
        search_params['filters'] = filters
        for order in order_by:
            order['field'] = _fix_field(order['field'])

        search_params['order_by'] = order_by

def facts_postproc(result=None, **kw):
    auth_values = current_user.approved_variables()
    for object in result.get('objects', []):
        for value in object.get('values', []).keys():
            if value not in auth_values:
                object['values'].pop(value, None)

preprocessors=dict(GET_SINGLE=[auth_func],
                   GET_MANY=[auth_func],
                   DELETE=[auth_admin],
                   PATCH_SINGLE=[auth_admin],
                   PATCH_MANY=[auth_admin],
                   POST=[auth_admin],
                  )

admin_only_proprocessors = dict(preprocessors)
admin_only_proprocessors['GET_SINGLE'] = [auth_admin]
admin_only_proprocessors['GET_MANY'] = [auth_admin]

def get_single_variable_preprocessor(instance_id=None, **kw):
    """Accepts a single argument, `instance_id`, the primary key of the
    instance of the model to get.

    """
    if instance_id not in current_user.approved_variables():
        raise ProcessingException('Access to ' + instance_id + ' not authorized.')

def get_many_variables_preprocessor(search_params=None, **kw):
    """Accepts a single argument, `search_params`, which is a dictionary
    containing the search parameters for the request.

    """
    # This checks if the preprocessor function is being called before a
    # request that does not have search parameters.
    if search_params is None:
        return
    # Create the filter you wish to add; in this case, we include only
    # instances with ``id`` not equal to 1.
    filt = dict(name='id', op='in', val=current_user.approved_variables())
    # Check if there are any filters there already.
    if 'filters' not in search_params:
        search_params['filters'] = []
    # *Append* your filter to the list of filters.
    search_params['filters'].append(filt)

manager.create_api(models.Dimension, 
                   methods=['GET', 'POST', 'DELETE', 'PUT'], 
                   results_per_page=RESULTS_PER_PAGE,
                   preprocessors=preprocessors)
manager.create_api(models.Variable, 
                   methods=['GET', 'POST', 'DELETE', 'PUT'], 
                   results_per_page=RESULTS_PER_PAGE,
                   preprocessors={'GET_SINGLE':[auth_func, get_single_variable_preprocessor],
                                  'GET_MANY':[auth_func, get_many_variables_preprocessor]
                                 })

facts_preprocessors = dict(preprocessors)
facts_preprocessors['GET_SINGLE'].append(facts_preproc)
facts_preprocessors['GET_MANY'].append(facts_preproc)
facts_postprocessors = {}
facts_postprocessors['GET_MANY'] = [facts_postproc]
facts_postprocessors['GET_SINGLE'] = [facts_postproc]
manager.create_api(models.Facts, 
                   methods=['GET', 'DELETE'],
                   results_per_page=RESULTS_PER_PAGE,
                   preprocessors=facts_preprocessors,
                   postprocessors=facts_postprocessors)
manager.create_api(models.Role, 
                   methods=['GET', 'POST', 'DELETE', 'PUT'],
                   results_per_page=RESULTS_PER_PAGE,
                   preprocessors=admin_only_proprocessors)
manager.create_api(models.Event, 
                   methods=['GET', 'POST', 'DELETE', 'PUT'],
                   results_per_page=RESULTS_PER_PAGE,
                   preprocessors=preprocessors)
manager.create_api(models.Source, 
                   methods=['GET', 'POST', 'DELETE', 'PUT'],
                   results_per_page=RESULTS_PER_PAGE,
                   preprocessors=preprocessors)
manager.create_api(models.Subject, 
                   methods=['GET', 'POST', 'DELETE', 'PUT'],
                   results_per_page=RESULTS_PER_PAGE,
                   preprocessors=admin_only_proprocessors)
manager.create_api(models.ExternalID, 
                   methods=['GET', 'POST', 'DELETE', 'PUT'],
                   results_per_page=RESULTS_PER_PAGE,
                   preprocessors=preprocessors)

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

