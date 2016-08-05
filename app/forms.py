from flask.ext.wtf import Form
from wtforms import StringField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length

class surveyForm(Form):
	# for page 3
	event = StringField('event', validators=[DataRequired()])
	# event = StringField('event')
	# location = StringField('location')
	# weather = StringField('weather')
	# style = StringField('style')

# class outfitcollection(Form):
class outfitForm(Form):
	# page 1
	outfit_one = TextAreaField('outfit_one')
	outfit_two = TextAreaField('outfit_two')
	outfit_three = TextAreaField('outfit_three')