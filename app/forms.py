from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, FileField
from wtforms.validators import DataRequired, ValidationError

from app.models import Item, Clay


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class AddItemForm(FlaskForm):
    clays = Clay.query.order_by('id')
    name = StringField('name', validators=[DataRequired()])
    clay_id_1 = SelectField('first clay', choices=[(c.id, c.name) for c in clays], validate_choice=False, coerce=int)
    clay_id_2 = SelectField('second clay',  choices=[(c.id, c.name) for c in clays], validate_choice=False, coerce=int)
    picture = FileField(u'Image File', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    submit = SubmitField('Add')

    def validate_name(self, name):
        item = Item.query.filter_by(name=name.data).first()
        if item is not None:
            raise ValidationError('Please use a different username.')
