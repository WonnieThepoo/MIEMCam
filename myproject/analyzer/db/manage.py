from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from application import create_app
from SQLAlcDataBase import db, User, TCam, Room

app = create_app()

migrate = Migrate(app, db)
manager = Manager(app)

# provide a migration utility command
manager.add_command('db', MigrateCommand)

# enable python shell with application context
@manager.shell
def shell_ctx():
    return dict(app=app,
                db=db,
                TCam=TCam,
                Room=Room,
                User=User)
if __name__ == "__main__":
    manager.run()


def move_abspantilt(self, pan, tilt, velocity):
    self.requesta.Position.PanTilt._x = pan
    self.requesta.Position.PanTilt._y = tilt
    self.requesta.Speed.PanTilt._x = velocity
    self.requesta.Speed.PanTilt._y = velocity
    print
    'Absolute move to:', self.requesta.Position
    print
    'Absolute speed:', self.requesta.Speed
    ret = self.ptz.AbsoluteMove(self.requesta)