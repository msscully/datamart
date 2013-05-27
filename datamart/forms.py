from flask.ext.wtf import Form, TextField, HiddenField, ValidationError,\
                          Required, validators
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from datamart import models

class ExampleForm(Form):
    field1 = TextField('First Field', description='This is field one.')
    field2 = TextField('Second Field', description='This is field two.',
                       validators=[Required()])
    hidden_field = HiddenField('You cannot see this', description='Nope')

    def validate_hidden_field(form, field):
        raise ValidationError('Always wrong')

class DimensionForm(Form):
    unit_name = TextField('Unit Name',
                          [validators.Required("Please enter a unit name.")],
                          description='A name for the unit of measurement. e.g. kg.')
    description = TextField('Description',
                            description='A human friendly description of the Dimension.')

def current_dimensions():
    return models.Dimension.query.all()

def current_roles():
    return models.Role.query.all()

class VariableForm(Form):
    display_name = TextField('Display Name',
                          [validators.Required("Please enter a display name.")],
                          description='A human friendly name to use for this variable.')
    description = TextField('Description',
                            description='A human friendly description of the Variable.')
    dimension = QuerySelectField(query_factory=current_dimensions, get_label='unit_name')
    roles = QuerySelectMultipleField(query_factory=current_roles, get_label='name')

class RoleForm(Form):
    name = TextField('Name',
                     [validators.Required("Please enter a display name.")],
                     description='A human friendly name to use for this role.')
    description = TextField('Description',
                            description='A human friendly description of this Role.')

