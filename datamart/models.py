from datamart import db

class Variable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(300), unique=True)
    display_name = db.Column(db.String(30), nullable=False, unique=True)
    id = db.Column(db.Integer, primary_key=True)
    min = db.Column(db.Float)
    max = db.Column(db.Float)
    std = db.Column(db.Float)
    mean = db.Column(db.Float)
    dimension_id = db.Column(db.Integer, db.ForeignKey('Dimension.id'))
    dimension = db.relationship('Dimension', backref=db.backref('variables', lazy='dynamic'))

    def __init__(self, display_name, dimension, description=None, min=None, max=None,
                 std=None, mean=None):
        self.description = description
        self.unit_name = display_name
        self.dimension = dimension
        self.min = min
        self.max = max
        self.mean = mean
        self.std = std

    def __repr__(self):
        repr = '<Variable %r - dim: %r, ' % (self.display_name, self.dimension)
        repr +=  'min: %r, max: %r, ' % (self.min, self.max)
        repr += 'mean: %r, std: %r>' % (self.mean, self.std)
        return repr

class Dimension(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(300), unique=True)
    unit_name = db.Column(db.String(30), nullable=False, unique=True)

    def __init__(self, unit_name, description=None, min=None, max=None,
                 std=None, mean=None):
        self.description = description
        self.unit_name = unit_name

    def __repr__(self):
        return '<Dimension %r>' % self.unit_name


