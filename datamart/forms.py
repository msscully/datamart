from flask.ext.wtf import Form, TextField, HiddenField, ValidationError,\
                          Required, validators
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from datamart import models, db
from wtforms.ext.sqlalchemy.orm import model_form

class ExampleForm(Form):
    field1 = TextField('First Field', description='This is field one.')
    field2 = TextField('Second Field', description='This is field two.',
                       validators=[Required()])
    hidden_field = HiddenField('You cannot see this', description='Nope')

    def validate_hidden_field(form, field):
        raise ValidationError('Always wrong')

DimensionForm = model_form(models.Dimension, db_session=db.session,
                           base_class=Form)

VariableForm = model_form(models.Variable, db_session=db.session, base_class=Form, 
                         field_args = {
                             'roles': {
                                 'get_label': 'name'
                             },
                             'dimension': {
                                 'get_label': 'unit_name'
                             }
                         })

RoleForm = model_form(models.Role, db_session=db.session, base_class=Form)
