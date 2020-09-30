from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    """
    Table of users
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    token = db.Column(db.VARCHAR(), nullable=False)
    cam = db.Column(db.Integer, nullable=True)
    presets = db.relationship('Presets', backref='user', lazy=False)

    def __init__(self, email, password, token, cam):
        self.email = email
        self.password = generate_password_hash(password, method='sha256')
        self.token = token
        self.cam = cam


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
    """
    Table of Presets
    """
    __tablename__ = 'presets'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    uid_cam = db.Column(db.Integer, nullable=False)
    button_clr = db.Column(db.String, nullable=True)
    preset_on_cam_id = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return dict(
            id=self.id,
            user_id=self.user_id,
            uid_cam=self.uid,
            button_clr=self.button_clr,
            preset_on_cam_id=self.preset_on_cam_id
        )
