from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    #cams = db.relationship('TCam', backref='user', lazy=False)

    def __init__(self, email, password):
        self.email = email
        self.password = generate_password_hash(password, method='sha256')

    @classmethod
    def authenticate(cls, **kwargs):
        email = kwargs.get('email')
        password = kwargs.get('password')

        if not email or not password:
            return None

        user = cls.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            return None

        return user

    def to_dict(self):
        return dict(id=self.id,
                    email=self.email,
                    cams=[post.to_dict() for post in self.posts] #доделать под себя
                    )

class TCam(db.Model):
    __tablename__ = 'tcams'

    uid = db.Column(db.String, unique=True, primary_key=True)
    ip = db.Column(db.String, nullable=True)
    port = db.Column(db.Integer, nullable=True)
    user = db.Column(db.String, nullable=True, default="admin")
    password = db.Column(db.String, nullable=True, default="Supervisor")
    name = db.Column(db.String, nullable = True)
    room =  db.Column(db.String, nullable = True)

    def to_dict(self):
        return dict(
            uid = self.uid,
            ip = self.ip,
            port = self.ip,
            user = self.user,
            passwrod = self.password,
            name = self.name,
            room = self.room)


class Room(db.Model):
    __tablename__ = 'rooms'

    id = db.Column(db.String, primary_key=True)
    cam_name = db.Column(db.String, nullable=True)
    uid = db.Column(db.String,  db.ForeignKey('cam_table.uid'), unique=True, nullable=True)
    #cam_table = db.relationship('Cam_table',  backref=db.backref('rooms', lazy=True))

    def to_dict(self):
        return dict(
            id = self.id,
            cam_name = self.cam_name,
            uid = self.uid,
            cam_table = self.cam_table
        )

"""class Cam_table(db.Model):
    __tablename__ = 'cam_table"""

