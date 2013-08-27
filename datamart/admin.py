from functools import wraps
from flask import request
from flask import redirect
from flask import url_for
from flask import flash
from flask.ext.security import current_user

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            if not current_user.is_authenticated:
                return redirect(url_for('security.login', next=request.url))
            else:
                flash('Permission denied.', 'alert-error')
                return redirect(request.referrer or url_for('datamart.index'))
        return f(*args, **kwargs)
    return decorated_function
