from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, FileField, RadioField
from wtforms.validators import DataRequired, ValidationError

from app.models import Item, Clay, Surface, Glaze

class MainForm(FlaskForm):

    clays = Clay.query.all()
    glazes = Glaze.query.all()
    surfaces = Surface.query.all()
    clay_filter = RadioField('Глина:', choices=[(c.id, c.name) for c in clays], coerce=int)
    surface_filter = RadioField('Поверхность:', choices=[(s.id, s.name) for s in surfaces], coerce=int)
    submit = SubmitField('Фильтр')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class AddItemForm(FlaskForm):
    clays = Clay.query.order_by('id')
    glazes = Glaze.query.order_by('id')
    surfaces = Surface.query.order_by('id')
    name = StringField('Название образца:', validators=[DataRequired()])
    glaze_id_1 = SelectField('Первая глазурь:', choices=[(c.id, c.name) for c in glazes], validate_choice=False,
                             coerce=int)
    glaze_id_2 = SelectField('Вторая глазурь:', choices=[(c.id, c.name) for c in glazes], validate_choice=False,
                             coerce=int)
    clay_id = SelectField('Глина:', choices=[(c.id, c.name) for c in clays], validate_choice=False, coerce=int)
    surface_id = SelectField('Поверхность:', choices=[(c.id, c.name) for c in surfaces], validate_choice=False,
                             coerce=int)
    image = FileField(u'Фото:', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    submit = SubmitField('Add')

    def validate_name(self, name):
        item = Item.query.filter_by(name=name.data).first()
        if item is not None:
            raise ValidationError('Please use a different username.')
