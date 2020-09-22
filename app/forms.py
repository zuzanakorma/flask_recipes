from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class LoginFoodForm(FlaskForm):
    food = StringField('Food', validators=[DataRequired()])
    time = StringField('Time', validators=[DataRequired()])
    temp = StringField('Temperature', validators=[DataRequired()])
    submit = SubmitField('Post')