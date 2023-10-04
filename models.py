from config import db
from flask_login import UserMixin


class Orders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer())
    title = db.Column(db.String(500))
    description = db.Column(db.String(15000))
    price = db.Column(db.String(50))
    status = db.Column(db.String(300))
    payment_status = db.Column(db.String(300))
    deadline = db.Column(db.String(50))
    date = db.Column(db.String(50))
    url = db.Column(db.String(50))
    git = db.Column(db.String(50))
    figma = db.Column(db.String(50))
    other = db.Column(db.String(5000))
    moderator_id = db.Column(db.Integer())
    design_id = db.Column(db.Integer())
    frontend_id = db.Column(db.Integer())
    backend_id = db.Column(db.Integer())
    admin_payment = db.Column(db.String(50))
    moderator_payment = db.Column(db.String(50))
    designer_payment = db.Column(db.String(50))
    frontend_payment = db.Column(db.String(50))
    backend_payment = db.Column(db.String(50))

    def __repr__(self):
        return f"<order {self.id}>"


class Requests(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(100))
    date = db.Column(db.String(50))
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(25))
    company = db.Column(db.String(500))
    message = db.Column(db.String(15000))
    moderator_id = db.Column(db.Integer)

    def __repr__(self):
        return f"<request {self.id}>"


class PaymentRequests(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer())
    status = db.Column(db.String(100))
    date = db.Column(db.String(50))
    name = db.Column(db.String(100))
    phone = db.Column(db.String(100))
    email = db.Column(db.String(100))
    amount = db.Column(db.String(500))
    telegram = db.Column(db.String(100))
    role = db.Column(db.String(25))
    details = db.Column(db.String(10000))
    comment = db.Column(db.String(10000))

    def __repr__(self):
        return f"<payment request {self.id}>"


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(64), unique=True)
    username = db.Column(db.String(200))
    password = db.Column(db.String(512), nullable=True)
    role = db.Column(db.String(100))
    email = db.Column(db.String(128))
    phone = db.Column(db.String(128))
    telegram = db.Column(db.String(128))
    other = db.Column(db.String(512))
    balance = db.Column(db.String(128))
    used_promocodes = db.Column(db.String(10000))

    def __init__(self, username, login, password, role, email, phone, telegram, other, balance):
        self.username = username
        self.password = password
        self.login = login
        self.role = role
        self.email = email
        self.phone = phone
        self.telegram = telegram
        self.other = other
        self.balance = balance

    def get_role(self):
        return self.role

    def __repr__(self):
        return f"<users {self.id}>"


class Promocodes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    promocode = db.Column(db.String(512))
    amount = db.Column(db.String(512))
    expire_date = db.Column(db.String(512))
    uses = db.Column(db.String(1024))

    def __repr__(self):
        return f"<promocode {self.id}>"


class ModeratorRequests(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(50))
    status = db.Column(db.String(100))
    moderator_id = db.Column(db.Integer)
    moderator_name = db.Column(db.String(500))
    order_id = db.Column(db.Integer)
    comment = db.Column(db.String(10000))
    admin_id = db.Column(db.Integer)
    admin_name = db.Column(db.String(256))
    admin_comment = db.Column(db.String(10000))
    answer_date = db.Column(db.String(50))

    def __repr__(self):
        return f"<Moderator requests {self.id}>"