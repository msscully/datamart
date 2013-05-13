from flask.ext.admin import Admin, BaseView, expose
from flask.ext.admin.contrib.sqlamodel import ModelView
from datamart import app, db, models

#TODO Make name configurable
admin = Admin(app, name='Datamart Admin', url='/admin')
admin.add_view(ModelView(models.Dimension, db.session))
admin.add_view(ModelView(models.Variable, db.session))
admin.add_view(ModelView(models.Facts, db.session))
