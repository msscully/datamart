from flask import render_template, request, flash, redirect, url_for,\
        jsonify, session, abort, current_app
from . import models
from .extensions import db
from . import forms
from .extensions import data_files
from .forms import RoleForm
from .forms import DimensionForm
from .forms import VariableForm
from .forms import UserForm
from .forms import FileUploadForm
from .forms import Form
from .forms import EventForm
from .forms import SourceForm
from .forms import SubjectForm
from .forms import ExternalIDForm
from .forms import IndvFactForm
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
from flask import Blueprint

datamart = Blueprint('datamart', __name__, template_folder='templates')

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

@datamart.route('/', methods=['GET', 'POST',])
def index():
    return render_template('index.html', login_user_form=LoginForm())

@datamart.route('/dimensions/', methods=['GET'])
@datamart.route('/dimensions/<int:dimension_id>/', methods=['GET'])
@login_required
def dimensions_view(dimension_id=None):
    return model_view(models.Dimension,'dimensions.html',dimension_id)

@datamart.route('/dimensions/add/', methods=['GET', 'POST'])
@datamart.route('/dimensions/<int:dimension_id>/edit/', methods=['GET', 'POST'])
@login_required
@admin_required
def dimension_edit(dimension_id=None):
    return model_edit(models.Dimension, 'dimension_edit.html', DimensionForm,
                      'dimensions_view', dimension_id)

@datamart.route('/variables/', methods=['GET'])
@datamart.route('/variables/<int:variable_id>/', methods=['GET'])
@login_required
def variables_view(variable_id=None):
    filter_clause = (models.Variable.id.in_(current_user.approved_variables()))
    return model_view(models.Variable,
                      'variables.html',
                      model_id=variable_id,
                      filter=filter_clause)

@datamart.route('/variables/add/', methods=['GET', 'POST'])
@datamart.route('/variables/<int:variable_id>/edit/', methods=['GET', 'POST'])
@login_required
@admin_required
def variable_edit(variable_id=None):
    return model_edit(models.Variable, 'variable_edit.html', VariableForm,
                      'variables_view', variable_id)

@datamart.route('/roles/', methods=['GET'])
@datamart.route('/roles/<int:role_id>/', methods=['GET'])
@login_required
@admin_required
def roles_view(role_id=None):
    return model_view(models.Role,'roles.html',role_id)

@datamart.route('/roles/add/', methods=['GET', 'POST'])
@datamart.route('/roles/<int:role_id>/edit/', methods=['GET', 'POST'])
@login_required
@admin_required
def role_edit(role_id=None):
    return model_edit(models.Role, 'role_edit.html', RoleForm,
                      'roles_view', role_id)

@datamart.route('/users/', methods=['GET'])
@datamart.route('/users/<int:user_id>/', methods=['GET'])
@login_required
@admin_required
def users_view(user_id=None):
    return model_view(models.User,'users.html',user_id)

@datamart.route('/users/add/', methods=['GET', 'POST'])
@datamart.route('/users/<int:user_id>/edit/', methods=['GET', 'POST'])
@login_required
@admin_required
def user_edit(user_id=None):
    return model_edit(models.User, 'user_edit.html', UserForm,
                      'users_view', user_id)

@datamart.route('/events/', methods=['GET'])
@datamart.route('/events/<int:event_id>/', methods=['GET'])
@login_required
def events_view(event_id=None):
    return model_view(models.Event,'events.html',event_id)

@datamart.route('/events/add/', methods=['GET', 'POST'])
@datamart.route('/events/<int:event_id>/edit/', methods=['GET', 'POST'])
@login_required
@admin_required
def event_edit(event_id=None):
    return model_edit(models.Event, 'event_edit.html', EventForm,
                      'events_view', event_id)

@datamart.route('/sources/', methods=['GET'])
@datamart.route('/sources/<int:source_id>/', methods=['GET'])
@login_required
def sources_view(source_id=None):
    return model_view(models.Source,'sources.html',source_id)

@datamart.route('/sources/add/', methods=['GET', 'POST'])
@datamart.route('/sources/<int:source_id>/edit/', methods=['GET', 'POST'])
@login_required
@admin_required
def source_edit(source_id=None):
    return model_edit(models.Source, 'source_edit.html', SourceForm,
                      'sources_view', source_id)


@datamart.errorhandler(404)
def not_found(error=None):
    message = {
            'status': 404,
            'message': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404

    return resp


@datamart.route('/facts/add/', methods=['GET', 'POST'])
@datamart.route('/facts/<int:fact_id>/edit/', methods=['GET', 'POST'])
@login_required
@admin_required
def fact_edit(fact_id=None):
    if fact_id:
        fact_data = models.Facts.query.get_or_404(fact_id)
    else:
        fact_data = models.Facts()
        fact_data.values = {}

    if fact_data.values:
        values = [{'variable_id': key, 'value': value} for (key, value) in fact_data.values.items()]
    else:
        values = []
    form = IndvFactForm(subject=fact_data.subject, 
                        event=fact_data.event,
                        values=values)

    subjects = models.Subject.query.order_by(models.Subject.internal_id).all()
    events = models.Event.query.order_by(models.Event.name).all()
    variables = models.variables_by_user()
    var_by_id = dict((str(var.id),var) for var in variables)

    if request.method == 'POST':
        if form.validate_on_submit():
            fact_data.subject_id = form.subject.data.id
            fact_data.event_id = form.event.data.id
            fact_values = {}
            for value in form.values:
                if value.variable_id.data != '':
                    fact_values[str(value.variable_id.data)] = value.value.data

            fact_data.values = fact_values
            db.session.add(fact_data)
            db.session.commit()

            if fact_id:
                flash('Fact updated!','alert-success')
            else:
                flash('New Fact added!', 'alert-success')
            redirect(url_for('fact_edit', fact_id=fact_data.id))
        else:
            for key in form.errors:
                if key == 'values':
                    for value_dict in form.errors[key]:
                        for value_key in value_dict:
                            for error in value_dict[value_key]:
                                flash("Error: " + error, "alert-error")
                else:
                    for error in form.errors[key]:
                        flash("Error: " + error, "alert-error")

            flash("Please fix errors and resubmit.", "alert-error")
            return render_template('fact_edit.html', 
                                   fact=fact_data,
                                   subjects=subjects,
                                   events=events,
                                   var_by_id=var_by_id,
                                   form=form
                                  )

    return render_template('fact_edit.html', 
                           fact=fact_data,
                           subjects=subjects,
                           events=events,
                           var_by_id=var_by_id,
                           form=form
                          )

@datamart.route('/facts/', methods=['GET'])
@login_required
def facts_view():
    facts = models.Facts.query.all()
    # select role.variables where role.users contains current_user
    variables = db.session.query(models.Variable).join((models.Role, models.Variable.roles))\
            .join((models.User,
                   models.Role.users)).filter(models.Variable.in_use == True,
                                              models.User.id == current_user.id)

    return render_template('facts.html', variables=variables, facts=facts)

@datamart.route('/facts/upload/label/<filename>/', methods=['GET', 'POST'])
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
                        if forms.is_type(int,column.lstrip()):
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
                        if forms.is_type(int,column.lstrip()):
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

@datamart.route('/facts/upload/', methods=['GET', 'POST'])
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

@datamart.route('/subjects/', methods=['GET'])
@datamart.route('/subjects/<int:subject_id>/', methods=['GET'])
@login_required
def subjects_view(subject_id=None):
    return model_view(models.Subject,'subjects.html',subject_id)

@datamart.route('/subjects/add/', methods=['GET', 'POST'])
@datamart.route('/subjects/<int:subject_id>/edit/', methods=['GET', 'POST'])
@login_required
@admin_required
def subject_edit(subject_id=None):
    return model_edit(models.Subject, 'subject_edit.html', SubjectForm,
                      'subjects_view', subject_id)

@datamart.route('/externalids/', methods=['GET'])
@datamart.route('/externalids/<int:externalid_id>/', methods=['GET'])
@login_required
def externalIDs_view(externalid_id=None):
    return model_view(models.ExternalID,'externalids.html',externalid_id)

@datamart.route('/externalids/add/', methods=['GET', 'POST'])
@datamart.route('/externalids/<int:externalid_id>/edit/', methods=['GET', 'POST'])
@login_required
def externalID_edit(externalid_id=None):
    return model_edit(models.ExternalID, 'externalid_edit.html', ExternalIDForm,
                      'externalIDs_view', externalid_id)


def get_facts_api_response(*args, **kwargs):
    #request.args.set('results_per_page', 100000)
    view = current_app.view_functions['factsapi0.factsapi']
    res = view(None,None)
    return res

@datamart.route('/facts/download/', methods=['GET'])
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
                if forms.is_type(int, row[column_index]):
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
                if forms.is_type(int, row[column_index]):
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
            if not forms.is_type(models.DATATYPES[variable.dimension.data_type],row[column_index]):
                field.errors.append('Not all data in Column ' +
                                    str(column_index+1) + ' can be cast to ' +
                                    variable.dimension.data_type + '.')
                return False

    return True
