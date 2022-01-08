from flask_wtf import FlaskForm as form
from wtforms import StringField, SubmitField, HiddenField
from wtforms.validators import DataRequired


class CreateForm(form):
    title = StringField('title', validators=[DataRequired()])
    category = StringField('category', validators=[DataRequired()])
    description = HiddenField("description")
    folder = HiddenField('folder')
    date = HiddenField('date')
    updated = HiddenField('updated')
    publish = SubmitField('Publish')
    draft = SubmitField('Draft')
