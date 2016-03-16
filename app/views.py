from flask import render_template, redirect, url_for, jsonify, request
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
		print(form.event.data)
		survey_result = Survey(event=form.event.data,
								location=form.location.data,
								weather=form.weather.data,
								style=form.style.data)
		db.session.add(survey_result)
		db.session.commit()

		mallet_runner_local()

		doctops_return = dict()
		with open("app/mallet/doctops", "r") as f:
			for i,l in enumerate(f):
				print(i,l)

		return redirect(url_for('index'))
	return render_template('page3.html', form=form)

@app.route('/page31', methods=['POST','GET'])
def survey2():
	print(request.form)
	form = surveyForm(request.form)
	print(form.event.data)
	survey_result = Survey(event=form.event.data,
							location=form.location.data,
							weather=form.weather.data,
							style=form.style.data)
	db.session.add(survey_result)
	db.session.commit()

	# mallet_runner_local()

	doctops_return = dict()
	# doctops_return = []
	with open("app/mallet/doctops", "r") as f:
		for i,l in enumerate(f):
			# print(i,l)
			doctops_return["line"+str(i)] = l
			# doctops_return.append({"line":l})

	return jsonify(doctops_return)

def mallet_runner_AWS():
	command1 = "/home/ubuntu/Ding/mallet-2.0.8RC3/bin/mallet import-file --input /home/ubuntu/Ding/FlaskDemo/app/mallet/words.txt --output /home/ubuntu/Ding/FlaskDemo/app/mallet/output.sequences --keep-sequence --token-regex '[\p{L}\p{P}\p{N}]*\p{L}' --use-pipe-from /home/ubuntu/Ding/FlaskDemo/app/mallet/training.sequences"
	command2 = "/home/ubuntu/Ding/mallet-2.0.8RC3/bin/mallet infer-topics --input /home/ubuntu/Ding/FlaskDemo/app/mallet/output.sequences --inferencer /home/ubuntu/Ding/FlaskDemo/app/mallet/inferencer.output.0 --output-doc-topics /home/ubuntu/Ding/FlaskDemo/app/mallet/doctops"

	command3 = "/home/ubuntu/Ding/mallet-2.0.8RC3/bin/mallet import-file --input /home/ubuntu/Ding/FlaskDemo/app/mallet/styles.txt --output /home/ubuntu/Ding/FlaskDemo/app/mallet/style_output.sequences --keep-sequence --token-regex '[\p{L}\p{P}\p{N}]*\p{L}' --use-pipe-from /home/ubuntu/Ding/FlaskDemo/app/mallet/descriptor.sequences"
	command4 = "/home/ubuntu/Ding/mallet-2.0.8RC3/bin/mallet infer-topics --input /home/ubuntu/Ding/FlaskDemo/app/mallet/style_output.sequences --inferencer /home/ubuntu/Ding/FlaskDemo/app/mallet/inferencer.output.1 --output-doc-topics /home/ubuntu/Ding/FlaskDemo/app/mallet/style_doctops"

	os.system(command1)
	print("done")
	os.system(command2)
	print("done2")

	os.system(command3)
	print("done3")
	os.system(command4)
	print("done4")
	return


def mallet_runner_local():
	command1 = "mallet-2.0.8RC3/bin/mallet import-file --input app/mallet/words.txt --output app/mallet/output.sequences --keep-sequence --token-regex '[\p{L}\p{P}\p{N}]*\p{L}' --use-pipe-from app/mallet/training.sequences"
	command2 = "mallet-2.0.8RC3/bin/mallet infer-topics --input app/mallet/output.sequences --inferencer app/mallet/inferencer.output.0 --output-doc-topics app/mallet/doctops"

	command3 = "mallet-2.0.8RC3/bin/mallet import-file --input app/mallet/styles.txt --output app/mallet/style_output.sequences --keep-sequence --token-regex '[\p{L}\p{P}\p{N}]*\p{L}' --use-pipe-from app/mallet/descriptor.sequences"
	command4 = "mallet-2.0.8RC3/bin/mallet infer-topics --input app/mallet/style_output.sequences --inferencer app/mallet/inferencer.output.1 --output-doc-topics app/mallet/doctops_style"

	os.system(command1)
	print("done")
	os.system(command2)
	print("done2")

	os.system(command3)
	print("done3")
	os.system(command4)
	print("done4")
	return

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

