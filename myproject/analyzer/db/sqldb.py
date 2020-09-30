from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    token = db.Column(db.VARCHAR())
    presets = db.relationship('Presets', backref='user', lazy=False)

    def __init__(self, email, password, token):
        self.email = email
        self.password = generate_password_hash(password, method='sha256')
        self.token = token

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
                    token=self.token,
                    presets=[preset.to_dict() for preset in self.presets]
                    )


class Presets(db.Model):
    __tablename__ = 'presets'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    uid_cam = db.Column(db.Integer, nullable=True)
    button_clr = db.Column(db.String)
    preset_on_cam_id = db.Column(db.Integer, nullable=True)

    def to_dict(self):
        return dict(
            id=self.id,
            user_id=self.user_id,
            uid_cam=self.uid,
            button_clr=self.button_clr,
            preset_on_cam_id=self.preset_on_cam_id
        )
