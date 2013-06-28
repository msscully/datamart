import flask.ext.restless
from flask import request, _request_ctx_stack, current_app
from datamart import app, db, models, security
import inspect
import sqlalchemy
from sqlalchemy.orm import ColumnProperty
from sqlalchemy.orm import object_mapper
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm.exc import UnmappedInstanceError
from flask.ext.restless import ProcessingException
from flask.ext.restless import helpers 
from flask.ext.security import current_user, utils
from flask.ext.security import login_required
from flask.ext.principal import Identity, identity_changed 
from flask.ext.security.decorators import BasicAuth
from sqlalchemy.orm.query import Query
from sqlalchemy.orm.util import class_mapper
import datetime
import uuid
 
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
    opfunc = flask.ext.restless.search.OPERATORS[operator]
    argspec = inspect.getargspec(opfunc)
    # in Python 2.6 or later, this should be `argspec.args`
    numargs = len(argspec[0])
    # raises AttributeError if `fieldname` or `relation` does not exist
    try:
        field = getattr(model, relation or fieldname)
    except AttributeError as attr_error:
        # Check if the field is in the values hstore
        valid_vars = current_user.approved_vars_and_datatypes()
        if (fieldname or relation) in valid_vars:
            field = model.values[relation or fieldname]
            # If it is we need to cast
            data_type = models.Variable.query.get(int(fieldname or relation)).dimension.data_type
            field = sqlalchemy.cast(field, DIMENSION_DATATYPES[data_type])
        else:
            raise attr_error

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

def search(session, model, search_params):
    """Performs the search specified by the given parameters on the model
    specified in the constructor of this class.

    This function essentially calls :func:`create_query` to create a query
    which matches the set of all instances of ``model`` which meet the search
    parameters defined in ``search_params``, then returns all results (or just
    one if ``search_params['single'] == True``).

    This function returns a single instance of the model matching the search
    parameters if ``search_params['single']`` is ``True``, or a list of all
    such instances otherwise. If ``search_params['single']`` is ``True``, then
    this method will raise :exc:`sqlalchemy.orm.exc.NoResultFound` if no
    results are found and :exc:`sqlalchemy.orm.exc.MultipleResultsFound` if
    multiple results are found.

    `model` is a SQLAlchemy declarative model class representing the database
    model to query.

    `search_params` is a dictionary containing all available search
    parameters. For more information on available search parameters, see
    :ref:`search`. Implementation note: this dictionary will be converted to a
    :class:`SearchParameters` object when the :func:`create_query` function is
    called.

    """
    # `is_single` is True when 'single' is a key in ``search_params`` and its
    # corresponding value is anything except those values which evaluate to
    # False (False, 0, the empty string, the empty list, etc.).
    is_single = search_params.get('single')
    query = flask.ext.restless.search.create_query(session, model, search_params)
    authorized_result = []
    if is_single:
        # may raise NoResultFound or MultipleResultsFound
        authorized_result = query.one()
    authorized_result = query.all()
    if hasattr(model, 'values'):
        valid_vars = current_user.approved_variables()
        for var in valid_vars:
            pass
    return authorized_result

flask.ext.restless.search.search = search
flask.ext.restless.views.search = search

def to_dict(instance, deep=None, exclude=None, include=None,
            exclude_relations=None, include_relations=None,
            include_methods=None):
    """Returns a dictionary representing the fields of the specified `instance`
    of a SQLAlchemy model.

    The returned dictionary is suitable as an argument to
    :func:`flask.jsonify`; :class:`datetime.date` and :class:`uuid.UUID`
    objects are converted to string representations, so no special JSON encoder
    behavior is required.

    `deep` is a dictionary containing a mapping from a relation name (for a
    relation of `instance`) to either a list or a dictionary. This is a
    recursive structure which represents the `deep` argument when calling
    :func:`!_to_dict` on related instances. When an empty list is encountered,
    :func:`!_to_dict` returns a list of the string representations of the
    related instances.

    If either `include` or `exclude` is not ``None``, exactly one of them must
    be specified. If both are not ``None``, then this function will raise a
    :exc:`ValueError`. `exclude` must be a list of strings specifying the
    columns which will *not* be present in the returned dictionary
    representation of the object (in other words, it is a
    blacklist). Similarly, `include` specifies the only columns which will be
    present in the returned dictionary (in other words, it is a whitelist).

    .. note::

       If `include` is an iterable of length zero (like the empty tuple or the
       empty list), then the returned dictionary will be empty. If `include` is
       ``None``, then the returned dictionary will include all columns not
       excluded by `exclude`.

    `include_relations` is a dictionary mapping strings representing relation
    fields on the specified `instance` to a list of strings representing the
    names of fields on the related model which should be included in the
    returned dictionary; `exclude_relations` is similar.

    `include_methods` is a list mapping strings to method names which will
    be called and their return values added to the returned dictionary.

    """
    if (exclude is not None or exclude_relations is not None) and \
            (include is not None or include_relations is not None):
        raise ValueError('Cannot specify both include and exclude.')
    # create a list of names of columns, including hybrid properties
    try:
        columns = [p.key for p in object_mapper(instance).iterate_properties
                   if isinstance(p, ColumnProperty)]
    except UnmappedInstanceError:
        return instance
    for parent in type(instance).mro():
        columns += [key for key, value in parent.__dict__.iteritems()
                    if isinstance(value, hybrid_property)]
    # filter the columns based on exclude and include values
    if exclude is not None:
        columns = (c for c in columns if c not in exclude)
    elif include is not None:
        columns = (c for c in columns if c in include)
    # create a dictionary mapping column name to value
    result = dict((col, getattr(instance, col)) for col in columns
                  if not (col.startswith('__') or col in helpers.COLUMN_BLACKLIST))
    # add any included methods
    if include_methods is not None:
        result.update(dict((method, getattr(instance, method)())
                           for method in include_methods
                           if not '.' in method))
    # Check for objects in the dictionary that may not be serializable by
    # default. Specifically, convert datetime and date objects to ISO 8601
    # format, and convert UUID objects to hexadecimal strings.
    for key, value in result.items():
        # TODO We can get rid of this when issue #33 is resolved.
        if isinstance(value, datetime.date):
            result[key] = value.isoformat()
        elif isinstance(value, uuid.UUID):
            result[key] = str(value)
        elif is_mapped_class(type(value)):
            result[key] = to_dict(value)
    # recursively call _to_dict on each of the `deep` relations
    deep = deep or {}
    for relation, rdeep in deep.iteritems():
        # Get the related value so we can see if it is None, a list, a query
        # (as specified by a dynamic relationship loader), or an actual
        # instance of a model.
        relatedvalue = getattr(instance, relation)
        if relatedvalue is None:
            result[relation] = None
            continue
        # Determine the included and excluded fields for the related model.
        newexclude = None
        newinclude = None
        if exclude_relations is not None and relation in exclude_relations:
            newexclude = exclude_relations[relation]
        elif (include_relations is not None and
              relation in include_relations):
            newinclude = include_relations[relation]
        # Determine the included methods for the related model.
        newmethods = None
        if include_methods is not None:
            newmethods = [method.split('.', 1)[1] for method in include_methods
                        if method.split('.', 1)[0] == relation]
        if helpers.is_like_list(instance, relation):
            result[relation] = [to_dict(inst, rdeep, exclude=newexclude,
                                        include=newinclude,
                                        include_methods=newmethods)
                                for inst in relatedvalue]
            continue
        # If the related value is dynamically loaded, resolve the query to get
        # the single instance.
        if isinstance(relatedvalue, Query):
            relatedvalue = relatedvalue.one()
        result[relation] = to_dict(relatedvalue, rdeep, exclude=newexclude,
                                   include=newinclude,
                                   include_methods=newmethods)
    if hasattr(instance, 'values'):
        valid_vars = current_user.approved_variables()
        valid_output_values = {}
        for var in valid_vars:
            valid_output_values[str(var)] = result['values'].get(str(var), '')
        result['values'] = valid_output_values

    return result

flask.ext.restless.helpers.to_dict = to_dict
flask.ext.restless.views.to_dict = to_dict

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
manager.create_api(models.Facts, 
                   methods=['GET', 'DELETE'],
                   results_per_page=RESULTS_PER_PAGE,
                   preprocessors=preprocessors)
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

