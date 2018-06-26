from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin

db = SQLAlchemy()
lm = LoginManager()


class User(UserMixin, db.Model):
    """
	Registered user information is stored in database.
	"""
    id = db.Column(db.Integer, primary_key=True)
    social_id = db.Column(db.String(200), nullable=False, unique=True)
    name = db.Column(db.String(64), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username


class Category(db.Model):
    """
	Registered item information is stored in database.
	"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False, unique=True)
    items = []

    def __repr__(self):
        return '<Category %r>' % self.name

    def as_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "items": [item.as_dict() for item in self.items]
        }


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False, unique=True)
    info = db.Column(db.Text, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'),
                            nullable=False)
    category = db.relationship('Category',
                               backref=db.backref('items', lazy=True))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return '<Item %r>' % self.name

    def as_dict(self):
        return {
            "id": self.id,
            "title": self.name,
            "description:": self.info,
            "cat_id": self.category_id
        }


@lm.user_loader
def load_user(id):
    return User.query.get(id)
