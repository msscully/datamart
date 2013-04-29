from flask import render_template
from datamart import app
from forms import ExampleForm

@app.route('/', methods=('GET', 'POST',))
def index():
    form = ExampleForm()
    if form.validate_on_submit():
        return "PASSED"
    return render_template('index.html', form=form)

@app.route('/dimensions', methods=('GET'))
def dimensions():
    return render_template('dimensions.html')

@app.route('/variables', methods=('GET'))
def variables():
    return render_template('variables.html')
