from functools import wraps
from flask import request
from flask import redirect
from flask import url_for
from flask.ext.security import current_user

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            return redirect(url_for('security.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function
