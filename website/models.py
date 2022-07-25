from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class Customer(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150))
    current_email = ""
    firstName = db.Column(db.String(747))
    lastName = db.Column(db.String(666))
    birthDate = db.Column(db.String(10))
    creationDate = db.Column(db.DateTime(timezone=True), default=func.now())
    admin_id = db.Column(db.Integer, db.ForeignKey("admin.id"))


class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(150))
    password = db.Column(db.String(150))
    customers = db.relationship("Customer")
    notes = db.relationship("Note")


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    admin_id = db.Column(db.Integer, db.ForeignKey("admin.id"))



