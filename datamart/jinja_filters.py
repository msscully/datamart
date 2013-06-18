from datamart import app
from flask.ext.security import current_user

def remove_invalid_vars(variables):
    filtered_variables = []
    approved_variables = current_user.approved_variables()
    for variable in variables:
        if str(variable.id) in approved_variables:
            filtered_variables.append(variable)

    return filtered_variables

app.jinja_env.filters['remove_invalid_vars'] = remove_invalid_vars
