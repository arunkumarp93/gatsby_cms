from flask_wtf import FlaskForm as form
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class FolderForm(form):
    repo = StringField('repo', validators=[DataRequired()])
    posts_folder = StringField('posts', validators=[DataRequired()])
    drafts_folder = StringField('draft', validators=[DataRequired()])
    submit = SubmitField('Save')
