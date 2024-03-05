from .config import db

class Users(db.Model):
    email = db.Column(db.String(120),primary_key=True)
    username = db.Column(db.String(80),nullable=True)
    password = db.Column(db.String(255),nullable=True)

    def __repr__(self):
        return self.username
