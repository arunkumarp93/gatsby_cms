from flask_wtf import FlaskForm as form
from wtforms import StringField, PasswordField, SubmitField, HiddenField
from wtforms.validators import DataRequired, required, InputRequired, EqualTo

class FolderForm(form):
    repo = StringField('repo', validators=[DataRequired()])
    posts_folder =  StringField('posts', validators=[DataRequired()])
    drafts_folder = StringField('draft', validators=[DataRequired()])
    submit = SubmitField('Save')
