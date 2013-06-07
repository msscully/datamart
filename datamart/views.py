from flask import render_template, request, flash, redirect, url_for,\
        jsonify, session, abort, current_app
from datamart import app, models, db, data_files
from forms import RoleForm, DimensionForm, VariableForm, UserForm, \
        FileUploadForm, Form, EventForm, SourceForm
from flask.ext.security import login_required, LoginForm, current_user
from flask.ext.restless.views import jsonify_status_code
from flask.ext.wtf import QuerySelectField, validators
from flask import send_file, Response
from secure_redirect import get_redirect_target, redirect_back
import csv
import re
import os
import json
import StringIO

def model_view(model, template, model_id=None):
    if model_id:
        models_data = [model.query.get_or_404(model_id)]
    else:
        models_data = model.query.all()
    return render_template(template, models_data=models_data)

def model_edit(model, template, FormType, redirect_default, model_id=None):
    if model_id:
        model_data = model.query.get_or_404(model_id)
    else:
        model_data = model()

    form = FormType(obj=model_data)
    if request.method == 'POST':
        if form.validate_on_submit():
            form.populate_obj(model_data)
            db.session.add(model_data)
            db.session.commit()
            flash(model.__tablename__.title() + " updated", "alert-success")
            return form.redirect(redirect_default)
        else:
            flash("Please fix errors and resubmit.", "alert-error")
            return render_template(template, model_data=model_data,
                                   form=form)
    elif request.method == 'GET':
        return render_template(template, model_data=model_data,
                               form=form, next=next)

@app.route('/', methods=['GET', 'POST',])
def index():
    return render_template('index.html', form=LoginForm())

@app.route('/dimensions/', methods=['GET'])
@app.route('/dimensions/<int:dimension_id>/', methods=['GET'])
@login_required
def dimensions_view(dimension_id=None):
    return model_view(models.Dimension,'dimensions.html',dimension_id)

@app.route('/dimensions/add/', methods=['GET', 'POST'])
@app.route('/dimensions/<int:dimension_id>/edit/', methods=['GET', 'POST'])
@login_required
def dimension_edit(dimension_id=None):
    return model_edit(models.Dimension, 'dimension_edit.html', DimensionForm,
                      'dimensions_view', dimension_id)

@app.route('/variables/', methods=['GET'])
@app.route('/variables/<int:variable_id>/', methods=['GET'])
@login_required
def variables_view(variable_id=None):
    return model_view(models.Variable,'variables.html',variable_id)

@app.route('/variables/add/', methods=['GET', 'POST'])
@app.route('/variables/<int:variable_id>/edit/', methods=['GET', 'POST'])
@login_required
def variable_edit(variable_id=None):
    return model_edit(models.Variable, 'variable_edit.html', VariableForm,
                      'variables_view', variable_id)

@app.route('/roles/', methods=['GET'])
@app.route('/roles/<int:role_id>/', methods=['GET'])
@login_required
def roles_view(role_id=None):
    return model_view(models.Role,'roles.html',role_id)

@app.route('/roles/add/', methods=['GET', 'POST'])
@app.route('/roles/<int:role_id>/edit/', methods=['GET', 'POST'])
@login_required
def role_edit(role_id=None):
    return model_edit(models.Role, 'role_edit.html', RoleForm,
                      'roles_view', role_id)

@app.route('/users/', methods=['GET'])
@app.route('/users/<int:user_id>/', methods=['GET'])
@login_required
def users_view(user_id=None):
    return model_view(models.User,'users.html',user_id)

@app.route('/users/add/', methods=['GET', 'POST'])
@app.route('/users/<int:user_id>/edit/', methods=['GET', 'POST'])
@login_required
def user_edit(user_id=None):
    return model_edit(models.User, 'user_edit.html', UserForm,
                      'users_view', user_id)

@app.route('/events/', methods=['GET'])
@app.route('/events/<int:event_id>/', methods=['GET'])
@login_required
def events_view(event_id=None):
    return model_view(models.Event,'events.html',event_id)

@app.route('/events/add/', methods=['GET', 'POST'])
@app.route('/events/<int:event_id>/edit/', methods=['GET', 'POST'])
@login_required
def event_edit(event_id=None):
    return model_edit(models.Event, 'event_edit.html', EventForm,
                      'events_view', event_id)

@app.route('/sources/', methods=['GET'])
@app.route('/sources/<int:source_id>/', methods=['GET'])
@login_required
def sources_view(source_id=None):
    return model_view(models.Source,'sources.html',source_id)

@app.route('/sources/add/', methods=['GET', 'POST'])
@app.route('/sources/<int:source_id>/edit/', methods=['GET', 'POST'])
@login_required
def source_edit(source_id=None):
    return model_edit(models.Source, 'source_edit.html', SourceForm,
                      'sources_view', source_id)


@app.errorhandler(404)
def not_found(error=None):
    message = {
            'status': 404,
            'message': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404

    return resp

@app.route('/facts/', methods=['GET'])
@login_required
def facts_view():
    facts = models.Facts.query.all()
    # select role.variables where role.users contains current_user
    variables = db.session.query(models.Variable).join((models.Role, models.Variable.roles))\
            .join((models.User,
                   models.Role.users)).filter(models.Variable.in_use == True,
                                              models.User.id == current_user.id)

    return render_template('facts.html', variables=variables, facts=facts)

@app.route('/facts/upload/label/<filename>/', methods=['GET', 'POST'])
@login_required
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
                                 get_label='name'))

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
                new_fact.values[str(form['column_' + str(i)].data.id)] = column.lstrip()
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

@app.route('/facts/upload/', methods=['GET', 'POST'])
@login_required
def upload():
    form = FileUploadForm()
    if form.validate_on_submit():
        filename = data_files.save(request.files[form.data_file.name])
        flash("File saved.")
        #with open(data_files.path(filename), 'rb') as csvfile:
        #    spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        session['useheader'] = form.header_row
        return redirect(url_for("label_upload_data", filename=filename))
    return render_template('upload.html', form=form)

def get_facts_api_response(*args, **kwargs):
    #request.args.set('results_per_page', 100000)
    print request
    view = current_app.view_functions['factsapi0.factsapi']
    res = view(None,None)
    return res

@app.route('/facts/download/', methods=['GET'])
@login_required
def download_facts():
    if request.args.get('filters'):
        filters = request.args.get('filters')
    if request.args.get('order_by'):
        order_by = request.args.get('filters')
    stuff = get_facts_api_response()
    fact_data = json.loads(stuff.data)
    response = Response()
    response.mimetype = 'text/csv'
    filename = 'FactData.csv'
    response.headers['Content-Disposition'] = 'attachment; filename="%s";' % filename
    response.headers['Content-Transfer-Encoding'] = 'binary'

    vars_by_user = models.variables_by_user()
    columns = dict((i.name,i.id) for i in vars_by_user)
    datatypes = dict((i.name,i.dimension.data_type) for i in vars_by_user)
    print columns
    output = StringIO.StringIO()

    writer = csv.writer(output)
    writer.writerow(columns.keys())
    for row in fact_data['objects']:
        new_row = []
        for col in columns.keys():
            col_key = str(columns[col])
            if col_key in row:
                if datatypes[col] == 'String':
                    new_row.append(json.dumps(row[col_key]))
                else:
                    new_row.append(row[col_key])
            else:
                new_row.append('')
        writer.writerow(new_row)

    response.data = output.getvalue()
    response.headers['Content-Length'] = len(response.data)
    response.set_cookie('fileDownload', 'true', path='/')
    return response

DATATYPES = {
    'String': str,
    'Integer': int,
    'Float': float,
    'Boolean': bool
}
