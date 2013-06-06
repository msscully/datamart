from datamart import db
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.dialects.postgresql import HSTORE, INET, ENUM
from flask.ext.security import RoleMixin, UserMixin, current_user

def variables_by_user():
    return db.session.query(Variable).join((Role, Variable.roles))\
            .join((User,
                   Role.users)).filter(Variable.in_use == True,
                                              User.id == current_user.id).all()

roles_users = db.Table('roles_users', 
                       db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
                      )

roles_variables = db.Table('roles_variables',
                           db.Column('variable_id', db.Integer(), db.ForeignKey('variable.id')),
                           db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
                          )

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=False)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean)
    confirmed_at = db.Column(db.DateTime())
    last_login_at = db.Column(db.DateTime())
    current_login_at = db.Column(db.DateTime())
    last_login_ip = db.Column(INET)
    current_login_ip = db.Column(INET)
    login_count = db.Column(db.Integer())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    def approved_variables(self):
        return self.approved_vars_and_datatypes().keys()

    def approved_vars_and_datatypes(self):
        valid_vars = {}

        for role in self.roles:
            for variable in role.variables:
                valid_vars[str(variable.id)] = variable.dimension.data_type

        return valid_vars


    def __repr__(self):
        return '<User username=%r, email=%r>' % (self.username, self.email)

class Dimension(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(300), unique=True)
    name = db.Column(db.String(30), nullable=False, unique=True)
    data_type = db.Column(ENUM("String","Integer","Boolean","Float", name="dim_data_type_enum"), nullable=False, default="String")

    def __repr__(self):
        return '<Dimension name=%r>' % self.name

class Variable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(300), unique=True, nullable=False)
    name = db.Column(db.String(30), nullable=False, unique=True)
    min = db.Column(db.Float, nullable=True)
    max = db.Column(db.Float, nullable=True)
    std = db.Column(db.Float, nullable=True)
    mean = db.Column(db.Float, nullable=True)
    # dimension is lowercase here as it's the table name, not the class name
    dimension_id = db.Column(db.Integer, db.ForeignKey('dimension.id'), nullable=False)
    # Here Dimension is upper case because it expects the class
    dimension = db.relationship('Dimension', backref=db.backref('variables', lazy='dynamic'))
    roles = db.relationship('Role', secondary=roles_variables,
                            backref='variables')
    in_use = db.Column(db.Boolean, default=True, nullable=False)

    def __repr__(self):
        repr = '<Variable name=%r - dim=%r>' % (self.name, self.dimension)
        return repr

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return '<Event id=%r, name=%r>' % (self.id, self.name)

class Facts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reviewed = db.Column(db.Boolean, nullable=False, default=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    event = db.relationship('Event')
    values = db.Column(MutableDict.as_mutable(HSTORE))

    def __repr__(self):
        return '<Fact id=%r>' % self.id
