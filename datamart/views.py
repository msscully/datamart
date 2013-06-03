from flask import render_template, request, flash, redirect, url_for,\
        jsonify, session, abort
from datamart import app, models, db, data_files
from forms import RoleForm, DimensionForm, VariableForm, UserForm, \
        FileUploadForm, Form
from flask.ext.security import login_required, LoginForm, current_user
from flask.ext.restless.views import jsonify_status_code
from flask.ext.wtf import QuerySelectField, validators
import csv
import re
import os

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
        dimensions = models.Dimension.query.order_by(models.Dimension.id)
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
        variables = models.Variable.query.order_by(models.Variable.id)
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

@app.route('/upload/label/<filename>', methods=['GET', 'POST'])
def label_upload_data(filename=None):
    try:
      with open(data_files.path(filename), 'rb') as csvfile:
          raw_data = csv.reader(csvfile, delimiter=',', quotechar='"')
          new_data = [i for i in raw_data]
    except IOError:
        abort(404)

    def is_type(type,s):
        try:
            type(s)
            return True
        except ValueError:
            return False

    top_ten = []
    for i, row in enumerate(new_data):
        if i >= 10: break
        top_ten.append(row)

    def column_datatype_check(form, field,data):
        m = re.search('_(\d+)',field.name)
        if m:
            column_index = int(m.group(1))
        else:
            raise Exception("Column doesn't have a numerical index?!")

        for row in data:
            print row
            print DATATYPES[field.data.dimension.data_type], row[column_index]
            if not is_type(DATATYPES[field.data.dimension.data_type],row[column_index]):
                field.errors.append('Not all data in Column ' + str(column_index+1) + ' can be cast to ' + field.data.dimension.data_type + '.')
                return False
        return True

    class F(Form):
        def __init__(self, data):
            super(F, self).__init__()
            self._data = data

        def validate(self):
            rv = Form.validate(self)
            if not rv:
                return False

            fields = (i for i in self.__dict__ if 'column_' in i)
            columns_valid = True
            for field in fields:
                print field
                if(not column_datatype_check(self,form[field],self._data)):
                    columns_valid = False
            if not columns_valid:
                return False
            return True


    for i,col in enumerate(top_ten[0]):
        setattr(F, 'column_' + str(i), 
                QuerySelectField('Variable type for Column ' + str(i+1),
                                 [validators.Required()],
                                 allow_blank=True, 
                                 blank_text=u'-- please choose --',
                                 get_label='display_name'))

    if session['useheader']:
        header_corrected_data = new_data[1:]
    else:
        header_corrected_data = new_data
    form = F(header_corrected_data)

    for i,col in enumerate(top_ten[0]):
        form['column_' + str(i)].query = models.variables_by_user() 

    if form.validate_on_submit():
        for row in header_corrected_data:
            new_fact = models.Facts()
            new_fact.values = {}
            for i,column in enumerate(row):
                new_fact.values[str(form['column_' + str(i)].data.id)] = column
            db.session.add(new_fact)
        db.session.commit()
        # Data has been committed so toss the uploaded file.
        os.remove(data_files.path(filename))

        flash('Variables Set and new data loaded!','alert-success')
        del session['useheader']
        return redirect(url_for('facts_view'))
    else:
        for key in form.errors:
            for error in form.errors[key]:
                flash("Error: " + error, "alert-error")
    return render_template('label_upload.html', data=top_ten, ind=1, form=form)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    form = FileUploadForm()
    if form.validate_on_submit():
        filename = data_files.save(request.files[form.data_file.name])
        flash("File saved.")
        with open(data_files.path(filename), 'rb') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
            session['useheader'] = form.header_row
            return redirect(url_for("label_upload_data", filename=filename))
    return render_template('upload.html', form=form)


DATATYPES = {
    'String': str,
    'Integer': int,
    'Float': float,
    'Boolean': bool
}
