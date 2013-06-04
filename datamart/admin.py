from flask.ext.admin import Admin, BaseView, expose
from flask.ext.admin.contrib.sqlamodel import ModelView
from datamart import app, db, models

#TODO Make name configurable
admin = Admin(app, name='Datamart Admin', url='/admin')
admin.add_view(ModelView(models.User, db.session))
admin.add_view(ModelView(models.Role, db.session))
