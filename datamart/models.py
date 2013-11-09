from .extensions import db
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.dialects.postgresql import HSTORE, INET, ENUM
from flask.ext.security import RoleMixin, UserMixin, current_user

DATATYPES = {
    'String': str,
    'Integer': int,
    'Float': float,
    'Boolean': bool
}

def variables_by_user():
    return db.session.query(Variable).join((Role, Variable.roles))\
            .join((User,
                   Role.users)).filter(Variable.in_use == True,
                                              User.id == current_user.id).order_by(Variable.name).all()

roles_users = db.Table('roles_users', 
                       db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
                      )

roles_variables = db.Table('roles_variables',
                           db.Column('variable_id', db.Integer(), db.ForeignKey('variable.id')),
                           db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
                          )

class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=False)

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean)
    confirmed_at = db.Column(db.DateTime())
    last_login_at = db.Column(db.DateTime())
    current_login_at = db.Column(db.DateTime())
    last_login_ip = db.Column(db.String(50))
    current_login_ip = db.Column(db.String(50))
    login_count = db.Column(db.Integer())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))
    is_admin = db.Column(db.Boolean, default=False)

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
    __tablename__ = 'dimension'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(300), unique=True)
    name = db.Column(db.String(30), nullable=False, unique=True)
    data_type = db.Column(ENUM("String","Integer","Boolean","Float", name="dim_data_type_enum"), nullable=False, default="String")

    def __repr__(self):
        return '<Dimension name=%r>' % self.name

class Variable(db.Model):
    __tablename__ = 'variable'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(300), nullable=False)
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
    in_use = db.Column(db.Boolean, default=True)

    def __repr__(self):
        repr = '<Variable name=%r - dim=%r>' % (self.name, self.dimension)
        return repr

sources_events = db.Table('sources_events', 
                       db.Column('source_id',
                                 db.Integer(),
                                 db.ForeignKey('source.id')),
                       db.Column('event_id',
                                 db.Integer(),
                                 db.ForeignKey('event.id'))
                      )

sources_variables = db.Table('sources_variables', 
                       db.Column('source_id',
                                 db.Integer(),
                                 db.ForeignKey('source.id')),
                       db.Column('variable_id',
                                 db.Integer(),
                                 db.ForeignKey('variable.id'))
                      )

class Event(db.Model):
    __tablename__ = 'event'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return '<Event id=%r, name=%r>' % (self.id, self.name)

class Source(db.Model):
    __tablename__ = 'source'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(255), nullable=True)
    events = db.relationship('Event', secondary=sources_events,
                            backref='sources')
    variables = db.relationship('Variable', secondary=sources_variables,
                            backref='sources')


    def __repr__(self):
        return '<Source id=%r, name=%r, url=%r>' % (self.id, self.name, self.url)

class Facts(db.Model):
    __tablename__ = 'facts'
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, 
                           db.ForeignKey('subject.id', ondelete='CASCADE'), 
                           nullable=False)
    subject = db.relationship('Subject')
    event_id = db.Column(db.Integer, 
                         db.ForeignKey('event.id', ondelete='CASCADE'), 
                         nullable=False)
    event = db.relationship('Event')
    values = db.Column(MutableDict.as_mutable(HSTORE))

    def __repr__(self):
        return '<Fact id=%r>' % self.id

class ExternalID(db.Model):
    __tablename__ = 'externalID'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    __table_args__ = (db.UniqueConstraint('subject_id', 'name',
                                       name='_subject_externalid_name_uc'),)

class Subject(db.Model):
    __tablename__ = 'subject'
    id = db.Column(db.Integer, primary_key=True)
    internal_id = db.Column(db.String(100), unique=True)
    external_ids = db.relationship('ExternalID', backref='subject')
