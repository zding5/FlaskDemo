from flask import render_template, redirect, url_for, jsonify
from app import app, db
from .models import Picture
import json

@app.route('/')
@app.route('/index')
def index():
	pics = Picture.query.all()
	return render_template('index.html', pics = pics)

@app.route('/populate', methods=['POST'])
def populate():
	if Picture.query.filter_by(link="f8d2a81b4c09364384a4322406ad47e8ce7ba38b.jpg").first() is None:
		u = Picture(name="Sheer jacket", link="f8d2a81b4c09364384a4322406ad47e8ce7ba38b.jpg")
		db.session.add(u)
		db.session.commit()
	# return json.dumps({'name':'Sheer jacket', 'id':'2', 'link':'f8d2a81b4c09364384a4322406ad47e8ce7ba38b.jpg'})
	return_data = {'name':'Sheer jacket', 'id':'2', 'link':'f8d2a81b4c09364384a4322406ad47e8ce7ba38b.jpg'}
	return jsonify(return_data)


@app.route('/deleter', methods=['DELETE'])
def delete():
	u = Picture.query.filter_by(link="f8d2a81b4c09364384a4322406ad47e8ce7ba38b.jpg").first()
	delid = u.id
	if u is not None:
		db.session.delete(u)
		db.session.commit()
	return jsonify({'delid':delid})

