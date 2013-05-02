from flask.ext.script import Manager, Server, Shell, prompt_pass
import datamart

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

#@manager.option('--user', '-u', dest='user')
#@manager.option('--email', '-e', dest='email')
#@manager.option('--admin', '-a', dest='admin', default=False, type=bool,
#                required=False, )
#def create_user(user, admin, email):
#    '''Create a new user in the application.'''
#    password = prompt_pass('New user password')
#    new_user = auth.User(username=user, admin=admin, active=True, email=email)
#    new_user.set_password(password)
#    new_user.save()

@manager.command
def create_tables():
    '''Create database tables.'''
    db.create_all()
    print('Database Created.')

if __name__ == "__main__":
    manager.add_command('shell', Shell(make_context=_shell_context, use_ipython=False))
    manager.run()