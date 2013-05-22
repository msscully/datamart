from flask import render_template, request, flash, redirect, url_for
from datamart import app, models, db
from forms import ExampleForm, DimensionForm

@app.route('/', methods=['GET', 'POST',])
def index():
    form = ExampleForm()
    if form.validate_on_submit():
        return "PASSED"
    return render_template('index.html', form=form)

@app.route('/dimensions', methods=['GET'])
@app.route('/dimensions/<int:dimension_id>', methods=['GET'])
def dimensions_view(dimension_id=None):
    if dimension_id:
        dimensions = [models.Dimension.query.get_or_404(dimension_id)]
    else:
        dimensions = models.Dimension.query.all()
    return render_template('dimensions.html', dimensions=dimensions)

@app.route('/dimensions/add', methods=['GET', 'POST'])
@app.route('/dimensions/<int:dimension_id>/edit', methods=['GET', 'POST'])
def dimension_edit(dimension_id=None):
    if dimension_id:
        dimension = models.Dimension.query.get_or_404(dimension_id)
    else:
        dimension = models.Dimension()

    form = DimensionForm(obj=dimension)
    if request.method == 'POST':
        if form.validate():
            form.populate_obj(dimension)
            db.session.add(dimension)
            db.session.commit()
            flash("Dimension updated", "alert-success")
            return redirect(url_for("dimensions_view", dimension_id=dimension_id))
        else:
            flash("Please populate required fields.", "alert-error")
            return render_template('dimension_edit.html', dimension=dimension,
                                   form=form)
    elif request.method == 'GET':
        return render_template('dimension_edit.html', dimension=dimension, form=form)

@app.route('/dimensions/<int:dimension_id>/delete', methods=['POST'])
def dimension_delete(dimension_id):
    dimension = models.Dimension.query.get_or_404(dimension_id)
    db.session.delete(dimension)
    db.session.commit()
    flash("Dimension " + dimension.unit_name + " succesfully deleted.", "alert-success")
    return render_template('dimensions_view')

@app.route('/variables', methods=['GET'])
def variables_view():
    return render_template('variables.html')
