from app import db
from app import app

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), index=True, unique=True)

	def __repr__(self):
		return '<User %r>' % (self.name)

class Picture(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), index=True, unique=True)
	link = db.Column(db.String(128), index=True, unique=True)
	# attributes = db.Column(db.String(128))

	def __repr__(self):
		return '<Pic #%r %r of link %r>' % (self.id, self.name, self.link)