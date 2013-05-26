from datamart import db
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.dialects.postgresql import HSTORE

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
    min = db.Column(db.Float, nullable=True)
    max = db.Column(db.Float, nullable=True)
    std = db.Column(db.Float, nullable=True)
    mean = db.Column(db.Float, nullable=True)
    # dimension is lowercase here as it's the table name, not the class name
    dimension_id = db.Column(db.Integer, db.ForeignKey('dimension.id'))
    # Here Dimension is upper case because it expects the class
    dimension = db.relationship('Dimension', backref=db.backref('variables', lazy='dynamic'))

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
