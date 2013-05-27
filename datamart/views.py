from flask import render_template, request, flash, redirect, url_for,\
        jsonify, json
from datamart import app, models, db
from forms import RoleForm, DimensionForm, VariableForm, UserForm
from flask.ext.security import login_required, LoginForm

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

@app.route('/api/facts/<int:id>', methods=['GET','PUT','PATCH','POST','DELETE'])
@login_required
def fact_api():
    pass

# Amazing http status code diagram: http://i.stack.imgur.com/whhD1.png
@app.route('/api/facts', methods=['GET','PUT','PATCH','POST','DELETE'])
@login_required
def facts_api():
    data = {'total_pages': 1,
            'num_results': 0,
            'page': 1,
            'items': []
           }

    if request.headers['Content-Type'] == 'application/json':
        if request.method == 'GET':
            resp = jsonify(data)
            resp.status_code = 200
            return resp

        elif request.method == 'POST':
            blah = request.json
            data['test'] = blah
            #message = jsonify(json.loads(request.data))
            resp = jsonify(data)
            resp.status_code = 201
            resp.location = url_for('fact_api', id=1)
            return resp

        elif request.method == 'PATCH':
            return "ECHO: PATCH\n"

        elif request.method == 'PUT':
            # if new item then 201
            resp = jsonify(data)
            resp.status_code = 201
            return resp

        elif request.method == 'DELETE':
            # If nothing in response body 204
            resp = jsonify({})
            resp.status_code = 204
            return resp

    else:
        message = {
            'status': 406,
            'message': 'Content-Type: \'' + request.headers['Content-Type'] + '\' not supported.'
        }
        resp = jsonify(message)
        resp.status_code = 406
        return resp
