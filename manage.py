from flask.ext.script import Manager, Server, Shell, prompt_pass
from flask.ext.alembic import ManageMigrations
from datamart import create_app
from datamart.extensions import db
from datamart.extensions import security
import flask_security
import os

app = create_app()
manager = Manager(app)

class DevServer(Server):
    def handle(self, app, host, port, use_debugger, use_reloader):

        app.run(host=host,
            port=port,
            debug=use_debugger,
            use_debugger=use_debugger,
            use_reloader=use_reloader,
            **self.server_options)

def _shell_context():
    return dict(app=app, db=db)        

@manager.command
def run():
    """Run in local machine."""

    app.run()

@manager.option('--with-coverage', '-c', dest='coverage', default=False,
                action='store_true', required=False)
def test(coverage):
    """Run test suite."""
    if coverage:
        os.system('nosetests --with-coverage --cover-package=datamart -s')
        pass
    else:
        os.system('nosetests -s')

@manager.option('--user', '-u', dest='user')
@manager.option('--email', '-e', dest='email')
@manager.option('--admin', '-a', dest='admin', default=False,
                action='store_true',
                required=False, )
def create_user(user, admin, email):
    '''Create a new user in the application.'''
    if not user:
        user = raw_input('Username: ')
    if not email:
        email = raw_input('email: ')
    password = flask_security.utils.encrypt_password(prompt_pass('New user password'))
    security.datastore.create_user(email=email, password=password, username=user,
                                   active=True, is_admin=admin)
    db.session.commit()

@manager.command
def create_tables():
    '''Create database tables.'''
    db.create_all()
    print('Database Created.')

@manager.command
def drop_db():
    '''Drop EVERYTHING in databse.'''
    #db.reflect()
    db.drop_all()
    print('Everything dropped from database.')

if __name__ == "__main__":
    manager.add_command('shell', Shell(make_context=_shell_context, use_ipython=True))
    manager.add_command("migrate", ManageMigrations())
    manager.run()
