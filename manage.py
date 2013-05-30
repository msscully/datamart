from flask.ext.script import Manager, Server, Shell, prompt_pass
import datamart
import os

app = datamart.app
db = datamart.db
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

@manager.option('--user', '-u', dest='user')
@manager.option('--email', '-e', dest='email')
@manager.option('--admin', '-a', dest='admin', default=False, type=bool,
                required=False, )
def create_user(user, admin, email):
    '''Create a new user in the application.'''
    password = prompt_pass('New user password')
    if not user:
        user = raw_input('Username: ')
    if not email:
        email = raw_input('email: ')
    datamart.user_datastore.create_user(email=email, password=password, username=user,
                               active=True)
    db.session.commit()

@manager.command
def create_tables():
    '''Create database tables.'''
    db.create_all()
    print('Database Created.')

if __name__ == "__main__":
    manager.add_command('shell', Shell(make_context=_shell_context, use_ipython=False))
    manager.run()
