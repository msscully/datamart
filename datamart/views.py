from flask import render_template
from datamart import app
from forms import ExampleForm

@app.route('/', methods=('GET', 'POST',))
def index():
    form = ExampleForm()
    if form.validate_on_submit():
        return "PASSED"
    return render_template('example.html', form=form)

