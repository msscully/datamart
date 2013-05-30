from flask import render_template, request, flash, redirect, url_for,\
        jsonify, json
from datamart import app, models, db, api
from forms import RoleForm, DimensionForm, VariableForm, UserForm
from flask.ext.security import login_required, LoginForm, current_user
from flask.ext.restless.views import jsonify_status_code
from operator import itemgetter
import math

@app.route('/', methods=['GET', 'POST',])
def index():
    return render_template('index.html', form=LoginForm())

@app.route('/dimensions', methods=['GET'])
@app.route('/dimensions/<int:dimension_id>', methods=['GET'])
@login_required
def dimensions_view(dimension_id=None):
    if dimension_id:
        dimensions = [models.Dimension.query.get_or_404(dimension_id)]
    else:
        dimensions = models.Dimension.query.all()
    return render_template('dimensions.html', dimensions=dimensions)

@app.route('/dimensions/add', methods=['GET', 'POST'])
@app.route('/dimensions/<int:dimension_id>/edit', methods=['GET', 'POST'])
@login_required
def dimension_edit(dimension_id=None):
    if dimension_id:
        dimension = models.Dimension.query.get_or_404(dimension_id)
    else:
        dimension = models.Dimension()

    form = DimensionForm(obj=dimension)
    if request.method == 'POST':
        if form.validate_on_submit():
            form.populate_obj(dimension)
            db.session.add(dimension)
            db.session.commit()
            flash("Dimension updated", "alert-success")
            return redirect(url_for("dimensions_view"))
        else:
            flash("Please fix errors and resubmit.", "alert-error")
            return render_template('dimension_edit.html', dimension=dimension,
                                   form=form)
    elif request.method == 'GET':
        return render_template('dimension_edit.html', dimension=dimension, form=form)

@app.route('/dimensions/<int:dimension_id>/delete', methods=['POST'])
@login_required
def dimension_delete(dimension_id):
    dimension = models.Dimension.query.get_or_404(dimension_id)
    db.session.delete(dimension)
    db.session.commit()
    flash("Dimension " + dimension.unit_name + " succesfully deleted.", "alert-success")
    return render_template('dimensions_view')

@app.route('/variables', methods=['GET'])
@app.route('/variables/<int:variable_id>', methods=['GET'])
@login_required
def variables_view(variable_id=None):
    if variable_id:
        variables = [models.Variable.query.get_or_404(variable_id)]
    else:
        variables = models.Variable.query.all()
    return render_template('variables.html', variables=variables)

@app.route('/variables/add', methods=['GET', 'POST'])
@app.route('/variables/<int:variable_id>/edit', methods=['GET', 'POST'])
@login_required
def variable_edit(variable_id=None):
    if variable_id:
        variable = models.Variable.query.get_or_404(variable_id)
    else:
        variable = models.Variable()

    form = VariableForm(obj=variable)
    if request.method == 'POST':
        if form.validate_on_submit():
            form.populate_obj(variable)
            variable.dimension_id = form.dimension.data.id
            db.session.add(variable)
            db.session.commit()
            flash("Variable updated", "alert-success")
            return redirect(url_for("variables_view"))
        else:
            flash("Please fix errors and resubmit.", "alert-error")
            return render_template('variable_edit.html', variable=variable,
                                   form=form)
    elif request.method == 'GET':
        return render_template('variable_edit.html', variable=variable, form=form)

@app.route('/roles', methods=['GET'])
@app.route('/roles/<int:role_id>', methods=['GET'])
@login_required
def roles_view(role_id=None):
    if role_id:
        roles = [models.Role.query.get_or_404(role_id)]
    else:
        roles = models.Role.query.all()
    return render_template('roles.html', roles=roles)

@app.route('/roles/add', methods=['GET', 'POST'])
@app.route('/roles/<int:role_id>/edit', methods=['GET', 'POST'])
@login_required
def role_edit(role_id=None):
    if role_id:
        role = models.Role.query.get_or_404(role_id)
    else:
        role = models.Role()

    form = RoleForm(obj=role)
    if request.method == 'POST':
        if form.validate_on_submit():
            form.populate_obj(role)
            db.session.add(role)
            db.session.commit()
            flash("Role updated", "alert-success")
            return redirect(url_for("roles_view"))
        else:
            flash("Please fix errors and resubmit.", "alert-error")
            return render_template('role_edit.html', role=role,
                                   form=form)
    elif request.method == 'GET':
        return render_template('role_edit.html', role=role, form=form)

@app.route('/users', methods=['GET'])
@app.route('/users/<int:user_id>', methods=['GET'])
@login_required
def users_view(user_id=None):
    if user_id:
        users = [models.User.query.get_or_404(user_id)]
    else:
        users = models.User.query.all()
    return render_template('users.html', users=users)

@app.route('/users/add', methods=['GET', 'POST'])
@app.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def user_edit(user_id=None):
    if user_id:
        user = models.User.query.get_or_404(user_id)
    else:
        user = models.User()

    form = UserForm(obj=user)
    if request.method == 'POST':
        if form.validate_on_submit():
            form.populate_obj(user)
            db.session.add(user)
            db.session.commit()
            flash("User updated", "alert-success")
            return redirect(url_for("users_view"))
        else:
            flash("Please fix errors and resubmit.", "alert-error")
            return render_template('user_edit.html', user=user,
                                   form=form)
    elif request.method == 'GET':
        return render_template('user_edit.html', user=user, form=form)


@app.errorhandler(404)
def not_found(error=None):
    message = {
            'status': 404,
            'message': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404

    return resp

@app.route('/facts', methods=['GET'])
@login_required
def facts_view():
    facts = models.Facts.query.all()
    # select role.variables where role.users contains current_user
    variables = db.session.query(models.Variable).join((models.Role, models.Variable.roles))\
            .join((models.User,
                   models.Role.users)).filter(models.Variable.in_use == True,
                                              models.User.id == current_user.id)

    return render_template('facts.html', variables=variables, facts=facts)

#@app.route('/api/facts/<int:id>', methods=['GET','PUT','PATCH','POST','DELETE'])
#@login_required
#def fact_api():
#    pass

## Amazing http status code diagram: http://i.stack.imgur.com/whhD1.png
#@app.route('/api/facts', methods=['GET','PUT','PATCH','POST','DELETE'])
##@login_required
#def facts_api():
#    data = {}
#
#    if request.headers['Content-Type'] == 'application/json':
#        if request.method == 'GET':
#            # try to get search query from the request query parameters
#            try:
#                search_params = json.loads(request.args.get('q', '{}'))
#            except (TypeError, ValueError, OverflowError), exception:
#                app.logger.exception(exception.message)
#                return jsonify_status_code(400, message='Unable to decode data')
#
#            facts = models.Facts.query.all()
#
#            # select role.variables where role.users contains current_user
#            variable_objs = db.session.query(models.Variable).join((models.Role, models.Variable.roles))\
#                    .join((models.User, models.Role.users)).filter(models.Variable.in_use == True,
#                                              models.User.id == 4)
#
#            variables = [str(var.id) for var in variable_objs]
#
#            if 'filters' in search_params:
#                for filter in search_params['filters']:
#                    pass
#
#            objects = []
#            for fact in facts:
#                values = fact.values
#                approved_fact = {}
#                approved_fact['id'] = str(fact.id)
#                approved_fact['reviewed'] = str(fact.reviewed)
#                for var in variables:
#                    new_val = {}
#                    if values and str(var) in values:
#                        new_val['value'] = values[str(var)]
#                    else:
#                        new_val['value'] = ''
#
#                    new_val['data_type'] = models.Variable.query.get(var).dimension.data_type
#                    approved_fact[str(var)] = new_val
#                objects.append(approved_fact)
#
#            #Pagination logic
#            num_results = len(facts)
#            results_per_page = api.compute_results_per_page()
#            if results_per_page > 0:
#                # get the page number (first page is page 1)
#                page_num = int(request.args.get('page', 1))
#                start = (page_num - 1) * results_per_page
#                end = min(num_results, start + results_per_page)
#                total_pages = int(math.ceil(float(num_results) / results_per_page))
#            else:
#                page_num = 1
#                start = 0
#                end = num_results
#                total_pages = 1
#            data['num_results'] = num_results
#            data['page'] = page_num
#            data['total_pages'] = total_pages
#
#            s = objects
#            if 'order_by' in search_params:
#                for order in reversed(search_params['order_by']):
#                    desc = True if order['direction'] == 'desc' else False
#                    if order['field'] in variables:
#                        data_type = DATATYPES[models.Variable.query.get(order['field']).dimension.data_type]
#                        s = sorted(s, key=lambda x:
#                                   data_type(x[order['field']]['value']), reverse=desc)
#                    elif getattr(models.Facts, str(order['field'])):
#                        s = sorted(s, key=itemgetter(order['field']), reverse=desc)
#                    else:
#                        # Return error
#                        pass
#
#
#            data['objects'] = [obj for obj in s[start:end]]
#
#            resp = jsonify(data)
#            resp.status_code = 200
#            return resp
#
#        elif request.method == 'POST':
#            #TODO Make this not suck
#            request_data = request.json
#            new_fact = models.Fact()
#            if 'reviewed' in request_data:
#                new_fact.reviewed = request_data['reviewed']
#            if 'values' in request_data:
#                new_fact.values = request_data['values']
#            resp = jsonify({})
#            resp.status_code = 201
#            resp.location = url_for('fact_api', id=new_fact.id)
#            return resp
#
#        elif request.method == 'PATCH':
#            return "ECHO: PATCH\n"
#
#        elif request.method == 'PUT':
#            #TODO make this add data
#            # if new item then 201
#            resp = jsonify(data)
#            resp.status_code = 201
#            return resp
#
#        elif request.method == 'DELETE':
#            #TODO Make this perform a delete.
#            # If nothing in response body 204
#            resp = jsonify({})
#            resp.status_code = 204
#            return resp
#
#    else:
#        message = {
#            'status': 406,
#            'message': 'Content-Type: \'' + request.headers['Content-Type'] + '\' not supported.'
#        }
#        resp = jsonify(message)
#        resp.status_code = 406
#        return resp
#
DATATYPES = {
    'String': str,
    'Int': int,
    'Float': float,
    'Bool': bool
}
