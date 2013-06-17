from flask.ext.wtf import Form
from flask.ext.wtf import validators
from flask.ext.wtf import FileField
from flask.ext.wtf import BooleanField
from datamart import models
from datamart import db
from wtforms.ext.sqlalchemy.orm import model_form
from secure_redirect import RedirectForm

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
