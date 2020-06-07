from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileRequired
from sqlalchemy import select
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, FileField, RadioField, \
    IntegerField, TextAreaField, SelectMultipleField
from wtforms.validators import DataRequired, ValidationError, Optional, length

from app.models import Item, Clay, Surface, Glaze, ItemGlaze
from app.utils import MultiCheckboxField


class ListForm(FlaskForm):
    def __init__(self, *args, **kwargs):
        super(ListForm, self).__init__(*args, **kwargs)
        glazes_choices = ([(0, 'Все')]).__add__([(c.id, c.name) for c in Glaze.query.order_by('id')])
        clays_choices = ([(0, 'Все')]).__add__([(c.id, c.name) for c in Clay.query.order_by('id')])
        surfaces_choices = ([(0, 'Все')]).__add__([(c.id, c.name) for c in Surface.query.order_by('id')])
        self.glaze_filter.choices = glazes_choices
        self.clay_filter.choices = clays_choices
        self.surface_filter.choices = surfaces_choices
    glaze_filter = SelectField('Глазурь:', choices=None, coerce=int, validators=[Optional()])
    clay_filter = SelectField('Глина:', choices=None, coerce=int, validators=[Optional()])
    surface_filter = SelectField('Поверхность:', choices=None, coerce=int, validators=[Optional()])
    submit = SubmitField('Фильтр')


class TableForm(FlaskForm):
    def __init__(self, *args, **kwargs):
        super(TableForm, self).__init__(*args, **kwargs)
        glazes = Glaze.query.order_by('id')
        glazes_choices = ([(0, 'Все')]).__add__([(c.id, c.name) for c in glazes])
        clays_choices = ([(0, 'Все')]).__add__([(c.id, c.name) for c in Clay.query.order_by('id')])
        surfaces_choices = ([(0, 'Все')]).__add__([(c.id, c.name) for c in Surface.query.order_by('id')])
        self.glazes = glazes
        self.glaze_filter.choices = glazes_choices
        self.clay_filter.choices = clays_choices
        self.surface_filter.choices = surfaces_choices

    glazes = None
    glaze_filter = SelectField('Глазурь:', choices=None, coerce=int, validators=[Optional()])
    clay_filter = SelectField('Глина:', choices=None, coerce=int, validators=[Optional()])
    surface_filter = SelectField('Поверхность:', choices=None, coerce=int, validators=[Optional()])
    submit = SubmitField('Фильтр')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class AddItemForm(FlaskForm):
    def __init__(self, item_id, *args, **kwargs):
        super(AddItemForm, self).__init__(*args, **kwargs)
        glazes_choices = [(c.id, c.name) for c in Glaze.query.order_by('id')]
        glazes_additional_choices = ([(0, '_нет_')]).__add__(glazes_choices)
        clays_choices = [(c.id, c.name) for c in Clay.query.order_by('id')]
        surfaces_choices = [(c.id, c.name) for c in Surface.query.order_by('id')]
        self.glaze_id_1.choices = glazes_choices
        self.glaze_id_2.choices = glazes_additional_choices
        self.glaze_id_3.choices = glazes_additional_choices
        self.clay_id.choices = clays_choices
        self.surface_id.choices = surfaces_choices

    name = StringField('Название пробника:', validators=[Optional()])
    description = TextAreaField('Описание:', validators=[Optional(), length(max=512)])
    temperature = IntegerField('Температура:', validators=[DataRequired()])
    glaze_id_1 = SelectField('Глазурь 1:', choices=None, validate_choice=False,
                             coerce=int)
    glaze_id_2 = SelectField('Глазурь 2:', choices=None, validate_choice=False,
                             coerce=int)
    glaze_id_3 = SelectField('Глазурь 3:', choices=None, validate_choice=False,
                             coerce=int)
    clay_id = SelectField('Глина:', choices=None, validate_choice=False, coerce=int)
    surface_id = SelectField('Поверхность:', choices=None, validate_choice=False,
                             coerce=int)
    image = FileField(u'Фото:', validators=[FileAllowed(['jpeg', 'jpg', 'png'], 'Images only!')])
    submit = SubmitField('Добавить')


class AddGlazeForm(FlaskForm):
    name = StringField('Название глазури:', validators=[DataRequired()])
    submit = SubmitField('Добавить')


class AddClayForm(FlaskForm):
    name = StringField('Название глины:', validators=[DataRequired()])
    submit = SubmitField('Добавить')
