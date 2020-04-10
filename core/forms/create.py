from flask_wtf import FlaskForm as form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, HiddenField
from wtforms.validators import DataRequired, required, InputRequired, EqualTo

class CreateForm(form):
    title = StringField('title', validators=[DataRequired()])
    category = StringField('category', validators=[DataRequired()])
    description=HiddenField("description")
    folder = HiddenField('folder')
    date = HiddenField('date')
    updated= HiddenField('updated')
    publish = SubmitField('Publish')
    draft = SubmitField('Draft')
