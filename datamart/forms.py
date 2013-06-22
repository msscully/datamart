from flask.ext.wtf import Form
from flask.ext.wtf import validators
from flask.ext.wtf import FileField
from flask.ext.wtf import BooleanField
from flask.ext.wtf import IntegerField
from flask.ext.wtf import TextField
from flask.ext.wtf import FieldList
from flask.ext.wtf import FormField
from datamart import models
from datamart import db
from wtforms.ext.sqlalchemy.orm import model_form
from wtforms.ext.sqlalchemy.orm import QuerySelectField
from wtforms import Form as WTForm
from wtforms.validators import ValidationError
from wtforms.validators import Required
from secure_redirect import RedirectForm
from flask.ext.security import current_user

def is_type(type,s):
    try:
        type(s)
        return True
    except ValueError:
        return False

def approved_var(form, field):
    if str(field.data) not in current_user.approved_variables():
        raise ValidationError('Variable %r does not exist.' % field.data)

class IndvVariableFactForm(WTForm):
    variable_id = IntegerField('',[approved_var, Required()])
    value = TextField('')

    def validate_value(form, field):
        variable = models.Variable.query.get(form.variable_id.data)
        data_type = variable.dimension.data_type
        if not is_type(models.DATATYPES[data_type],field.data):
            raise ValidationError("Value for variable, \"" + variable.name + "\" can't be converted to data type, \"" + data_type + "\"")


def current_subjects():
    return models.Subject.query.order_by(models.Subject.internal_id)

def current_events():
    return models.Event.query.order_by(models.Event.name)

class IndvFactForm(RedirectForm):
    subject = QuerySelectField(query_factory=current_subjects,
                                  get_label='internal_id')
    event = QuerySelectField(query_factory=current_events, 
                                get_label='name')
    values = FieldList(FormField(IndvVariableFactForm))

    def get_value_errors(self):
        errors_dict = {}
        for value in self.values:
            errors_dict[str(value.variable_id.data)] = value.errors
        return errors_dict

class FileUploadForm(RedirectForm):
    header_row = BooleanField('Is the first column header names?')
    create_subjects = BooleanField("Create subjects if they don't already exist?")
    create_events = BooleanField("Create events if they don't already exist?")
    data_file = FileField()

DimensionForm = model_form(models.Dimension, db_session=db.session,
                           base_class=RedirectForm, exclude = ['variables'])

VariableForm = model_form(models.Variable, db_session=db.session, base_class=RedirectForm, 
                         field_args = {
                             'roles': {
                                 'get_label': 'name'
                             },
                             'dimension': {
                                 'get_label': 'name'
                             },
                             'sources': {
                               'get_label': 'name'
                             }
                         })

RoleForm = model_form(models.Role, db_session=db.session, base_class=RedirectForm)

EventForm = model_form(models.Event, db_session=db.session,
                       base_class=RedirectForm,
                       field_args = {
                           'sources': {
                               'get_label': 'name'
                           }
                       }
                      )

UserForm = model_form(models.User, db_session=db.session, base_class=RedirectForm,
                     exclude = ['confirmed_at',
                                'last_login_at',
                                'current_login_at',
                                'last_login_ip',
                                'current_login_ip',
                                'login_count'],
                     field_args = {
                         'roles': {
                             'get_label': 'name'
                         },
                         'email': {
                             'validators': [validators.Required(), validators.Email()]
                         }
                     })

SourceForm = model_form(models.Source, db_session=db.session, base_class=RedirectForm,
                     field_args = {
                         'url': {
                             'validators': [validators.URL()]
                         },
                         'events': {
                             'get_label': 'name'
                         },
                         'variables': {
                             'get_label': 'name'
                         },
                     })

ExternalIDForm = model_form(models.ExternalID, db_session=db.session,
                            base_class=RedirectForm,
                            field_args = {
                                'subject': {
                                    'get_label': 'internal_id'
                                },
                                'name': {
                                    'label': 'External ID'
                                }
                            })

SubjectForm = model_form(models.Subject, db_session=db.session, base_class=RedirectForm)
