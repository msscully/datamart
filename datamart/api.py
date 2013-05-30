import flask.ext.restless
from flask import request
from datamart import app, db, models
import inspect
import sqlalchemy
from flask.ext.restless import search, ProcessingException
from flask.ext.security import current_user
 
DIMENSION_DATATYPES = {
    'String': sqlalchemy.String,
    'Int': sqlalchemy.Integer,
    'Float': sqlalchemy.Float,
    'Bool': sqlalchemy.Boolean
}

@staticmethod
def _create_operation(model, fieldname, operator, argument, relation=None):
    """Translates an operation described as a string to a valid SQLAlchemy
    query parameter using a field or relation of the specified model.

    More specifically, this translates the string representation of an
    operation, for example ``'gt'``, to an expression corresponding to a
    SQLAlchemy expression, ``field > argument``. The recognized operators
    are given by the keys of :data:`OPERATORS`. For more information on
    recognized search operators, see :ref:`search`.

    If `relation` is not ``None``, the returned search parameter will
    correspond to a search on the field named `fieldname` on the entity
    related to `model` whose name, as a string, is `relation`.

    `model` is an instance of a SQLAlchemy declarative model being
    searched.

    `fieldname` is the name of the field of `model` to which the operation
    will be applied as part of the search. If `relation` is specified, the
    operation will be applied to the field with name `fieldname` on the
    entity related to `model` whose name, as a string, is `relation`.

    `operation` is a string representating the operation which will be
     executed between the field and the argument received. For example,
     ``'gt'``, ``'lt'``, ``'like'``, ``'in'`` etc.

    `argument` is the argument to which to apply the `operator`.

    `relation` is the name of the relationship attribute of `model` to
    which the operation will be applied as part of the search, or ``None``
    if this function should not use a related entity in the search.

    This function raises the following errors:
    * :exc:`KeyError` if the `operator` is unknown (that is, not in
      :data:`OPERATORS`)
    * :exc:`TypeError` if an incorrect number of arguments are provided for
      the operation (for example, if `operation` is `'=='` but no
      `argument` is provided)
    * :exc:`AttributeError` if no column with name `fieldname` or
      `relation` exists on `model`

    """
    # raises KeyError if operator not in OPERATORS
    opfunc = search.OPERATORS[operator]
    argspec = inspect.getargspec(opfunc)
    # in Python 2.6 or later, this should be `argspec.args`
    numargs = len(argspec[0])
    # raises AttributeError if `fieldname` or `relation` does not exist
    try:
        field = getattr(model, relation or fieldname)
    except AttributeError as a:
        # Check if the field is in the values hstore
        valid_vars = current_user.approved_vars_and_datatypes()
        if (fieldname or relation) in valid_vars:
            field = model.values[relation or fieldname]
            # If it is we need to cast
            data_type = models.Variable.query.get(int(fieldname or relation)).dimension.data_type
            field = sqlalchemy.cast(field, DIMENSION_DATATYPES[data_type])
        else:
            raise a

    # each of these will raise a TypeError if the wrong number of argments
    # is supplied to `opfunc`.
    if numargs == 1:
        return opfunc(field)
    if argument is None:
        raise TypeError
    if numargs == 2:
        return opfunc(field, argument)
    return opfunc(field, argument, fieldname)

flask.ext.restless.search.QueryBuilder._create_operation = _create_operation

@staticmethod
def create_query(session, model, search_params):
    """Builds an SQLAlchemy query instance based on the search parameters
    present in ``search_params``, an instance of :class:`SearchParameters`.

    This method returns a SQLAlchemy query in which all matched instances
    meet the requirements specified in ``search_params``.

    `model` is SQLAlchemy declarative model on which to create a query.

    `search_params` is an instance of :class:`SearchParameters` which
    specify the filters, order, limit, offset, etc. of the query.

    Building the query proceeds in this order:
    1. filtering the query
    2. ordering the query
    3. limiting the query
    4. offsetting the query

    Raises one of :exc:`AttributeError`, :exc:`KeyError`, or
    :exc:`TypeError` if there is a problem creating the query. See the
    documentation for :func:`_create_operation` for more information.

    """
    # Adding field filters
    query = flask.ext.restless.helpers.session_query(session, model)
    # may raise exception here
    filters = flask.ext.restless.search.QueryBuilder._create_filters(model, search_params)
    query = query.filter(search_params.junction(*filters))

    # Order the search
    for val in search_params.order_by:
        try:
            field = getattr(model, val.field)
        except AttributeError as a:
            # Check if the field is in the values hstore
            valid_vars = current_user.approved_vars_and_datatypes()
            if val.field in valid_vars:
                field = model.values[val.field]
                # If it is we need to cast
                data_type = models.Variable.query.get(int(val.field)).dimension.data_type
                field = sqlalchemy.cast(field, DIMENSION_DATATYPES[data_type])
            else:
                raise a

        direction = getattr(field, val.direction)
        query = query.order_by(direction())

    # Limit it
    if search_params.limit:
        query = query.limit(search_params.limit)
    if search_params.offset:
        query = query.offset(search_params.offset)
    return query

flask.ext.restless.search.QueryBuilder.create_query = create_query

RESULTS_PER_PAGE = 20
MAX_RESULTS_PER_PAGE = 300
manager = flask.ext.restless.APIManager(app, flask_sqlalchemy_db=db)
 
def auth_func(**kw):
   if not current_user.is_authenticated():
       raise ProcessingException(message='Not authenticated!')

preprocessors=dict(GET_SINGLE=[auth_func], GET_MANY=[auth_func])

manager.create_api(models.Dimension, 
                   methods=['GET', 'POST', 'DELETE', 'PUT'], 
                   results_per_page=RESULTS_PER_PAGE,
                   preprocessors=preprocessors)
manager.create_api(models.Variable, 
                   methods=['GET', 'POST', 'DELETE', 'PUT'], 
                   results_per_page=RESULTS_PER_PAGE,
                   preprocessors=preprocessors)
manager.create_api(models.Facts, 
                   methods=['GET'],
                   results_per_page=RESULTS_PER_PAGE,
                   preprocessors=preprocessors)
manager.create_api(models.Role, 
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

