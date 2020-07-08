from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileRequired
from sqlalchemy import select
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, FileField, RadioField, \
    IntegerField, TextAreaField, SelectMultipleField
from wtforms.validators import DataRequired, ValidationError, Optional, length, EqualTo, Email

from app.models import Item, Clay, Surface, Glaze, ItemGlaze, User


class ListForm(FlaskForm):
    def __init__(self, *args, **kwargs):
        super(ListForm, self).__init__(*args, **kwargs)
        glazes_choices = ([(0, 'Все')]).__add__([(c.id, c.name) for c in current_user.get_materials(Glaze)])
        clays_choices = ([(0, 'Все')]).__add__([(c.id, c.name) for c in current_user.get_materials(Clay)])
        surfaces_choices = ([(0, 'Все')]).__add__([(c.id, c.name) for c in current_user.get_surfaces()])
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
        glazes = current_user.get_materials(Glaze)
        glazes_choices = ([(0, 'Все')]).__add__([(c.id, c.name) for c in glazes])
        clays_choices = ([(0, 'Все')]).__add__([(c.id, c.name) for c in current_user.get_materials(Clay)])
        surfaces_choices = ([(0, 'Все')]).__add__([(c.id, c.name) for c in current_user.get_surfaces()])
        self.glazes = glazes
        self.glaze_filter.choices = glazes_choices
        self.clay_filter.choices = clays_choices
        self.surface_filter.choices = surfaces_choices

    glazes = None
    glaze_filter = SelectField('Глазурь:', choices=None, coerce=int, validators=[Optional()])
    clay_filter = SelectField('Глина:', choices=None, coerce=int, validators=[Optional()])
    surface_filter = SelectField('Поверхность:', choices=None, coerce=int, validators=[Optional()])
    submit = SubmitField('Фильтр')


class ItemForm(FlaskForm):
    submit = SubmitField('Фильтр')


class AddItemForm(FlaskForm):
    def __init__(self, item_id, *args, **kwargs):
        super(AddItemForm, self).__init__(*args, **kwargs)
        glazes_choices = [(c.id, c.name) for c in current_user.get_materials(Glaze)]
        glazes_additional_choices = ([(0, '_нет_')]).__add__(glazes_choices)
        clays_choices = [(c.id, c.name) for c in current_user.get_materials(Clay)]
        surfaces_choices = [(c.id, c.name) for c in current_user.get_surfaces()]
        self.glaze_id_1.choices = glazes_choices
        self.glaze_id_2.choices = glazes_additional_choices
        self.glaze_id_3.choices = glazes_additional_choices
        self.clay_id.choices = clays_choices
        self.surface_id.choices = surfaces_choices

    name = StringField('Название пробника:', validators=[Optional(), length(max=256)])
    description = TextAreaField('Описание:', validators=[Optional(), length(max=512)])
    is_public = BooleanField('Публичный доступ:')
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
    name = StringField('Название глазури:', validators=[DataRequired(), length(max=64)])
    submit = SubmitField('Добавить')


class AddClayForm(FlaskForm):
    name = StringField('Название глины:', validators=[DataRequired(), length(max=64)])
    submit = SubmitField('Добавить')


class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password2 = PasswordField(
        'Снова пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Зарегистрироваться')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Такое имя уже используется.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Такой адрес уже используется.')