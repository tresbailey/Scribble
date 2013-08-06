
from scribble import app
from flask.ext.script import Manager

manager = Manager(app)

@manager.command
def base():
    app.run(port=5000)

@manager.command
def second():
    app.run(port=5001)

if __name__ == "__main__":
    manager.run()
