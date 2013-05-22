from flask.ext.wtf import Form, TextField, HiddenField, ValidationError,\
                          Required, validators
from wtforms.ext.sqlalchemy.fields import QuerySelectField
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

