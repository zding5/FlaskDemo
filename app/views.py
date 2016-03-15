from flask import render_template, redirect, url_for, jsonify
from app import app, db
from .models import Picture, Survey
from .forms import surveyForm
import json
import os

@app.route('/')
@app.route('/index')
def index():
	pics = Picture.query.all()
	return render_template('index.html', pics = pics)



@app.route('/page3', methods=['GET','POST'])
def survey():
	form = surveyForm()
	if form.validate_on_submit():
		survey_result = Survey(event=form.event.data,
								location=form.location.data,
								weather=form.weather.data,
								style=form.style.data)
		db.session.add(survey_result)
		db.session.commit()
		# os.system('echo "Hello!" ')
		# tempstring = "boot jacket leather studded t-shirt black commando distressed fishnet alexander-mcqueen sweatshirt-hoodies"
		# with open("output.txt", "w+") as f:
			# f.write(tempstring)

		# command1 = "/home/dddg/mallet-2.0.8RC3/bin/mallet import-file --input app/mallet/output.txt --output output.sequences --keep-sequence --token-regex '[\p{L}\p{P}\p{N}]*\p{L}' --use-pipe-from app/mallet/training.sequences"
		# command1 = "mallet-2.0.8RC3/bin/mallet import-file --input app/mallet/words.txt --output app/mallet/output.sequences --keep-sequence --token-regex '[\p{L}\p{P}\p{N}]*\p{L}' --use-pipe-from app/mallet/training.sequences"
		# command2 = "/home/dddg/mallet-2.0.8RC3/bin/mallet infer-topics --input output.sequences --inferencer app/mallet/inferencer.output.0 --output-doc-topics doctops"
		# command2 = "mallet-2.0.8RC3/bin/mallet infer-topics --input app/mallet/output.sequences --inferencer app/mallet/inferencer.output.0 --output-doc-topics doctops"

		# command1 = "mallet-2.0.8RC3/bin/mallet import-file --input app/mallet/words.txt --output app/mallet/output.sequences --keep-sequence --token-regex '[\p{L}\p{P}\p{N}]*\p{L}' --use-pipe-from app/mallet/training.sequences"
		command1 = "/home/dddg/mallet-2.0.8RC3/bin/mallet import-file --input app/mallet/words.txt --output app/mallet/output.sequences --keep-sequence --token-regex '[\p{L}\p{P}\p{N}]*\p{L}' --use-pipe-from app/mallet/training.sequences"
		# command2 = "mallet-2.0.8RC3/bin/mallet infer-topics --input app/mallet/output.sequences --inferencer app/mallet/inferencer.output.0 --output-doc-topics app/mallet/doctops"
		command2 = "/home/dddg/mallet-2.0.8RC3/bin/mallet infer-topics --input app/mallet/output.sequences --inferencer app/mallet/inferencer.output.0 --output-doc-topics app/mallet/doctops"


		os.system(command1)
		print("done")
		os.system(command2)
		print("done2")
		return redirect(url_for('index'))
	return render_template('page3.html', form=form)


@app.route('/populate', methods=['POST'])
def populate():
	if Picture.query.filter_by(link="f8d2a81b4c09364384a4322406ad47e8ce7ba38b.jpg").first() is None:
		u = Picture(name="Sheer jacket", link="f8d2a81b4c09364384a4322406ad47e8ce7ba38b.jpg")
		db.session.add(u)
		db.session.commit()
	return_data = {'name':'Sheer jacket', 'id':'2', 'link':'f8d2a81b4c09364384a4322406ad47e8ce7ba38b.jpg'}
	return jsonify(return_data)


# @app.route('/deleter', methods=['DELETE'])
# def delete():
# 	u = Picture.query.filter_by(link="f8d2a81b4c09364384a4322406ad47e8ce7ba38b.jpg").first()
# 	delid = u.id
# 	if u is not None:
# 		db.session.delete(u)
# 		db.session.commit()
# 	return jsonify({'delid':delid})

