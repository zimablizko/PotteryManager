from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileRequired
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, FileField, RadioField, \
    IntegerField, TextAreaField, SelectMultipleField
from wtforms.validators import DataRequired, ValidationError, Optional, length

from app.models import Item, Clay, Surface, Glaze
from app.utils import MultiCheckboxField


class MainForm(FlaskForm):
    clays = [(c.id, c.name) for c in Clay.query.all()]
    glazes = Glaze.query.order_by('id')
    surfaces = [(c.id, c.name) for c in Surface.query.order_by('id')]
    clay_filter = RadioField('Глина:', choices=clays, coerce=int)
    surface_filter = RadioField('Поверхность:', choices=surfaces, coerce=int)
    submit = SubmitField('Фильтр')


class ListForm(FlaskForm):
    clays = [(c.id, c.name) for c in Clay.query.all()]
    glazes = [(c.id, c.name) for c in Glaze.query.order_by('id')]
    surfaces = [(c.id, c.name) for c in Surface.query.order_by('id')]
    glaze_filter = MultiCheckboxField('Глазурь:', choices=glazes, coerce=int, validators=[Optional()])
    clay_filter = MultiCheckboxField('Глина:', choices=clays, coerce=int, validators=[Optional()])
    surface_filter = MultiCheckboxField('Поверхность:', choices=surfaces, coerce=int, validators=[Optional()])
    submit = SubmitField('Фильтр')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class AddItemForm(FlaskForm):
    clays = [(c.id, c.name) for c in Clay.query.order_by('id')]
    glazes = [(c.id, c.name) for c in Glaze.query.order_by('id')]
    glazes_additional = ([(0, '_нет_')]).__add__(glazes)
    surfaces = [(c.id, c.name) for c in Surface.query.order_by('id')]
    name = StringField('Название пробника:', validators=[Optional()])
    description = TextAreaField('Описание:', validators=[Optional(), length(max=512)])
    temperature = IntegerField('Температура:', validators=[DataRequired()])
    glaze_id_1 = SelectField('Глазурь 1:', choices=glazes, validate_choice=False,
                             coerce=int)
    glaze_id_2 = SelectField('Глазурь 2:', choices=glazes_additional, validate_choice=False,
                             coerce=int)
    glaze_id_3 = SelectField('Глазурь 3:', choices=glazes_additional, validate_choice=False,
                             coerce=int)
    clay_id = SelectField('Глина:', choices=clays, validate_choice=False, coerce=int)
    surface_id = SelectField('Поверхность:', choices=surfaces, validate_choice=False,
                             coerce=int)
    image = FileField(u'Фото:', validators=[FileRequired(), FileAllowed(['jpeg', 'jpg', 'png'], 'Images only!')])
    submit = SubmitField('Добавить')

    # def validate_name(self, name):
    #     item = Item.query.filter_by(name=name.data).first()
    #     if item is not None:
    #         raise ValidationError('Please use a different username.')
