from flask.ext.wtf import Form, TextField, HiddenField, ValidationError,\
                          Required, validators, FileField, BooleanField
from datamart import models, db
from wtforms.ext.sqlalchemy.orm import model_form

class ExampleForm(Form):
    field1 = TextField('First Field', description='This is field one.')
    field2 = TextField('Second Field', description='This is field two.',
                       validators=[Required()])
    hidden_field = HiddenField('You cannot see this', description='Nope')

    def validate_hidden_field(form, field):
        raise ValidationError('Always wrong')

class FileUploadForm(Form):
    header_row = BooleanField('Is the first column header names?')
    data_file = FileField()

DimensionForm = model_form(models.Dimension, db_session=db.session,
                           base_class=Form, exclude = ['variables'])

VariableForm = model_form(models.Variable, db_session=db.session, base_class=Form, 
                         field_args = {
                             'roles': {
                                 'get_label': 'name'
                             },
                             'dimension': {
                                 'get_label': 'name'
                             }
                         })

RoleForm = model_form(models.Role, db_session=db.session, base_class=Form)

UserForm = model_form(models.User, db_session=db.session, base_class=Form,
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
