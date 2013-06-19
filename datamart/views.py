from flask import render_template, request, flash, redirect, url_for,\
        jsonify, session, abort, current_app
from datamart import app, models, db, data_files
from forms import RoleForm
from forms import DimensionForm
from forms import VariableForm
from forms import UserForm
from forms import FileUploadForm
from forms import Form
from forms import EventForm
from forms import SourceForm
from forms import SubjectForm
from forms import ExternalIDForm
from flask.ext.security import login_required, LoginForm, current_user
from flask.ext.restless.views import jsonify_status_code
from flask.ext.wtf import QuerySelectField
from flask.ext.wtf import SelectField
from flask.ext.wtf import validators
from flask import Response
from admin import admin_required
import csv
import re
import os
import json
import StringIO

def model_view(model, template, model_id=None, filter=None):
    if model_id:
        models_data = [model.query.get_or_404(model_id)]
    else:
        if filter is not None:
            models_data = model.query.filter(filter).all()
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
    return render_template('index.html', login_user_form=LoginForm())

@app.route('/dimensions/', methods=['GET'])
@app.route('/dimensions/<int:dimension_id>/', methods=['GET'])
@login_required
def dimensions_view(dimension_id=None):
    return model_view(models.Dimension,'dimensions.html',dimension_id)

@app.route('/dimensions/add/', methods=['GET', 'POST'])
@app.route('/dimensions/<int:dimension_id>/edit/', methods=['GET', 'POST'])
@login_required
@admin_required
def dimension_edit(dimension_id=None):
    return model_edit(models.Dimension, 'dimension_edit.html', DimensionForm,
                      'dimensions_view', dimension_id)

@app.route('/variables/', methods=['GET'])
@app.route('/variables/<int:variable_id>/', methods=['GET'])
@login_required
def variables_view(variable_id=None):
    filter_clause = (models.Variable.id.in_(current_user.approved_variables()))
    return model_view(models.Variable,
                      'variables.html',
                      model_id=variable_id,
                      filter=filter_clause)

@app.route('/variables/add/', methods=['GET', 'POST'])
@app.route('/variables/<int:variable_id>/edit/', methods=['GET', 'POST'])
@login_required
@admin_required
def variable_edit(variable_id=None):
    return model_edit(models.Variable, 'variable_edit.html', VariableForm,
                      'variables_view', variable_id)

@app.route('/roles/', methods=['GET'])
@app.route('/roles/<int:role_id>/', methods=['GET'])
@login_required
@admin_required
def roles_view(role_id=None):
    return model_view(models.Role,'roles.html',role_id)

@app.route('/roles/add/', methods=['GET', 'POST'])
@app.route('/roles/<int:role_id>/edit/', methods=['GET', 'POST'])
@login_required
@admin_required
def role_edit(role_id=None):
    return model_edit(models.Role, 'role_edit.html', RoleForm,
                      'roles_view', role_id)

@app.route('/users/', methods=['GET'])
@app.route('/users/<int:user_id>/', methods=['GET'])
@login_required
@admin_required
def users_view(user_id=None):
    return model_view(models.User,'users.html',user_id)

@app.route('/users/add/', methods=['GET', 'POST'])
@app.route('/users/<int:user_id>/edit/', methods=['GET', 'POST'])
@login_required
@admin_required
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
@admin_required
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
@admin_required
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
@admin_required
def label_upload_data(filename=None):
    try:
      with open(data_files.path(filename), 'rb') as csvfile:
          raw_data = csv.reader(csvfile, delimiter=',', quotechar='"',
                                skipinitialspace=True)
          new_data = [i for i in raw_data]
    except IOError:
        abort(404)

    if 'useheader' in session and session['useheader']:
        header_corrected_data = new_data[1:]
        headers = new_data[0]
    else:
        header_corrected_data = new_data
        headers = None

    top_ten = []
    for i, row in enumerate(header_corrected_data):
        if i >= 10: break
        top_ten.append(row)

    class FactsUploadForm(Form):
        def __init__(self, data):
            super(FactsUploadForm, self).__init__()
            self._data = data

        def validate(self):
            rv = Form.validate(self)
            if not rv:
                return False

            fields = (i for i in self.__dict__ if 'column_' in i)
            columns_valid = True
            subjects_present = False
            events_present = False
            for field in fields:
                if form[field].data == 'subjects':
                    subjects_present = True
                elif form[field].data == 'events':
                    events_present = True
                if(not column_datatype_check(self,form[field],self._data)):
                    columns_valid = False
            if not (subjects_present and events_present):
                flash('A Subjects and Events column must be present.','alert-error')
                return False
            if not columns_valid:
                return False
            return True

    select_options_sorted = get_label_select_options()
    for i,col in enumerate(top_ten[0]):
        setattr(FactsUploadForm, 'column_' + str(i), 
                SelectField('Variable type for Column ' + str(i+1),
                                 [validators.Required()],
                            choices=select_options_sorted
                           ))

    form = FactsUploadForm(header_corrected_data)

    if form.validate_on_submit():
        for row in header_corrected_data:
            new_fact = models.Facts()
            new_fact.values = {}
            for i,column in enumerate(row):
                var = str(form['column_' + str(i)].data)
                # This assumes events and subjects columns use db internal IDs.
                if var == 'events':
                    event_id = ''
                    if 'createevents' in session and session['createevents'] == True:
                        if models.Event.query.filter(models.Event.name == column.lstrip()).count() > 0:
                            event_id = models.Event.query.filter(models.Event.name == column.lstrip()).one().id
                        else:
                            new_event = models.Event()
                            new_event.name = column.lstrip()
                            db.session.add(new_event)
                            db.session.flush()
                            event_id = new_event.id
                    else:
                        # All subjects exist, as we've passed validation.
                        if is_type(int,column.lstrip()):
                            event_id = models.Event.query.get(column.lstrip()).id
                        else:
                            event_id = models.Event.query.filter(models.Event.name == column.lstrip()).one().id
                    new_fact.event_id = event_id
                if var == 'subjects':
                    subject_id = ''
                    if 'createsubjects' in session and session['createsubjects'] == True:
                        if models.Subject.query.filter(models.Subject.internal_id==column.lstrip()).count() > 0:
                            subject_id = models.Subject.query.filter(models.Subject.internal_id==column.lstrip()).one().id
                        else:
                            new_subject = models.Subject()
                            new_subject.internal_id = column.lstrip()
                            db.session.add(new_subject)
                            db.session.flush()
                            subject_id = new_subject.id
                    else:
                        # All subjects exist, as we've passed validation.
                        if is_type(int,column.lstrip()):
                            subject_id = models.Subject.query.get(column.lstrip()).id
                        else:
                            subject_id = models.Subject.query.filter(models.Subject.internal_id==column.lstrip()).one().id

                    new_fact.subject_id = subject_id
                else:
                    new_fact.values[var] = column.lstrip()
            db.session.add(new_fact)
        db.session.commit()
        # Data has been committed so toss the uploaded file.
        os.remove(data_files.path(filename))

        success_message = 'Variables set'
        if 'createsubjects' in session and session['createsubjects']:
            success_message = success_message + ", subjects created"
        if 'createevents' in session and session['createevents']:
            success_message = success_message + ", events created"
        success_message = success_message + ' and new data loaded!'
        flash(success_message,'alert-success')
        del session['useheader']
        del session['createsubjects']
        del session['createevents']
        return redirect(url_for('facts_view'))
    else:
        for key in form.errors:
            for error in form.errors[key]:
                flash("Error: " + error, "alert-error")
    return render_template('label_upload.html', data=top_ten, ind=1, form=form,
                          headers=headers)

@app.route('/facts/upload/', methods=['GET', 'POST'])
@login_required
@admin_required
def upload():
    form = FileUploadForm()
    if form.validate_on_submit():
        filename = data_files.save(request.files[form.data_file.name])
        flash("File saved.")
        #with open(data_files.path(filename), 'rb') as csvfile:
        #    spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        session['useheader'] = form.header_row.data
        session['createsubjects'] = form.create_subjects.data
        session['createevents'] = form.create_events.data
        return redirect(url_for("label_upload_data", filename=filename))
    return render_template('upload.html', form=form)

@app.route('/subjects/', methods=['GET'])
@app.route('/subjects/<int:subject_id>/', methods=['GET'])
@login_required
def subjects_view(subject_id=None):
    return model_view(models.Subject,'subjects.html',subject_id)

@app.route('/subjects/add/', methods=['GET', 'POST'])
@app.route('/subjects/<int:subject_id>/edit/', methods=['GET', 'POST'])
@login_required
@admin_required
def subject_edit(subject_id=None):
    return model_edit(models.Subject, 'subject_edit.html', SubjectForm,
                      'subjects_view', subject_id)

@app.route('/externalids/', methods=['GET'])
@app.route('/externalids/<int:externalid_id>/', methods=['GET'])
@login_required
def externalIDs_view(externalid_id=None):
    return model_view(models.ExternalID,'externalids.html',externalid_id)

@app.route('/externalids/add/', methods=['GET', 'POST'])
@app.route('/externalids/<int:externalid_id>/edit/', methods=['GET', 'POST'])
@login_required
def externalID_edit(externalid_id=None):
    return model_edit(models.ExternalID, 'externalid_edit.html', ExternalIDForm,
                      'externalIDs_view', externalid_id)


def get_facts_api_response(*args, **kwargs):
    #request.args.set('results_per_page', 100000)
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

def get_label_select_options():
    select_options = [(str(g.id), g.name) for g in models.variables_by_user()]
    select_options.extend([('subjects','Subjects'),('events','Events')])
    select_options_sorted = [('','')]
    select_options_sorted.extend(sorted(select_options, key=lambda var: var[1]))
    return select_options_sorted

def column_datatype_check(form, field,data):
    m = re.search('_(\d+)',field.name)
    if m:
        column_index = int(m.group(1))
    else:
        raise Exception("Column doesn't have a numerical index?!")

    for row in data:
        if field.data == 'subjects':
            # Did they give us DB IDs, internal_ids, or external_ids?
            if 'createsubjects' not in session or session['createsubjects'] != True:
                # All subjects must already exist.
                if is_type(int, row[column_index]):
                    if not models.Subject.query.get(row[column_index]):
                        field.errors.append('Not all data in Column ' +
                                            str(column_index+1) + 
                                            ' is a valid Subject ID or internal ID') 
                        return False
                elif not models.Subject.query.filter(models.Subject.internal_id == row[column_index].lstrip()).count() > 0:
                    field.errors.append('Not all data in Column ' +
                                        str(column_index+1) + 
                                        ' is a valid Subject ID or internal ID') 
                    return False

            else:
                # The subjects column must contain internal_ids, which are
                # strings, so no validation needed.
                pass
        elif field.data == 'events':
            # Did they give us DB IDs, or event.name(s)?
            if 'createevents' not in session or session['createevents'] != True:
                # All events must already exist.
                if is_type(int, row[column_index]):
                    if not models.Event.query.get(row[column_index]):
                        field.errors.append('Not all data in Column ' +
                                            str(column_index+1) + 
                                            ' is a valid Event ID or name.') 
                        return False
                elif models.Event.query.filter(models.Event.name == row[column_index].lstrip()).count() == 0:
                    field.errors.append('Not all data in Column ' +
                                        str(column_index+1) + 
                                        ' is a valid Event ID or name.') 
                    return False
            else:
                # The events column must contain event names, which are
                # strings, so no validation needed.
                pass
        else:
            variable = models.Variable.query.get(field.data)
            if not is_type(DATATYPES[variable.dimension.data_type],row[column_index]):
                field.errors.append('Not all data in Column ' +
                                    str(column_index+1) + ' can be cast to ' +
                                    variable.dimension.data_type + '.')
                return False

    return True

def is_type(type,s):
    try:
        type(s)
        return True
    except ValueError:
        return False


