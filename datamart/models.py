from datamart import db
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.dialects.postgresql import HSTORE, INET
from flask.ext.security import RoleMixin, UserMixin

roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer(),
                                 db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer(),
                                 db.ForeignKey('role.id')))

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    last_login_at = db.Column(db.DateTime())
    current_login_at = db.Column(db.DateTime())
    last_login_ip = db.Column(INET)
    current_login_ip = db.Column(INET)
    login_count = db.Column(db.Integer())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    def approved_variables(self):
        valid_vars = []

        for role in self.roles:
            for variable in role.variables:
                valid_vars.append(variable.id)

        return valid_vars

    def __repr__(self):
        return 'User %r, %r' % (self.username, self.email)

class Dimension(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(300), unique=True)
    unit_name = db.Column(db.String(30), nullable=False, unique=True)

    def __repr__(self):
        return 'Dimension %r' % self.unit_name

class Variable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(300), unique=True)
    display_name = db.Column(db.String(30), nullable=False, unique=True)
    id = db.Column(db.Integer, primary_key=True)
    min = db.Column(db.Float, nullable=True)
    max = db.Column(db.Float, nullable=True)
    std = db.Column(db.Float, nullable=True)
    mean = db.Column(db.Float, nullable=True)
    # dimension is lowercase here as it's the table name, not the class name
    dimension_id = db.Column(db.Integer, db.ForeignKey('dimension.id'))
    # Here Dimension is upper case because it expects the class
    dimension = db.relationship('Dimension', backref=db.backref('variables', lazy='dynamic'))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    role = db.relationship('Role', backref=db.backref('variables', lazy='dynamic'))

    def __repr__(self):
        repr = 'Variable %r - dim: %r, ' % (self.display_name, self.dimension)
        repr +=  'min: %r, max: %r, ' % (self.min, self.max)
        repr += 'mean: %r, std: %r' % (self.mean, self.std)
        return repr

class Facts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reviewed = db.Column(db.Boolean, nullable=False, default=False)
    values = db.Column(MutableDict.as_mutable(HSTORE))

    def __repr__(self):
        return 'Fact %r' % self.id
