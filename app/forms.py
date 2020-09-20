from datetime import datetime

from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileRequired
from sqlalchemy import select, desc
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, FileField, RadioField, \
    IntegerField, TextAreaField, SelectMultipleField, FieldList
from wtforms.validators import DataRequired, ValidationError, Optional, length, EqualTo, Email

from app.models import Item, Clay, Surface, Glaze, ItemGlaze, User


class ItemsForm(FlaskForm):
    def get_public_items(self):
        return Item.query.filter(Item.delete_date == None).filter(Item.is_public == True).order_by(desc(Item.edit_date))

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
        self.glaze_list[0].choices = glazes_choices
        self.glaze_list[1].choices = glazes_additional_choices
        self.glaze_list[2].choices = glazes_additional_choices
        self.clay_id.choices = clays_choices
        self.surface_id.choices = surfaces_choices

    name = StringField('Название пробника:', validators=[Optional(), length(max=256)])
    description = TextAreaField('Описание:', validators=[Optional(), length(max=500)])
    is_public = BooleanField('Публичный доступ:')
    temperature = IntegerField('Температура:', validators=[DataRequired()])
    glaze_list = FieldList(SelectField('Глазурь:', choices=None, validate_choice=False,
                             coerce=int), min_entries=3)
    clay_id = SelectField('Глина:', choices=None, validate_choice=False, coerce=int)
    surface_id = SelectField('Поверхность:', choices=None, validate_choice=False,
                             coerce=int)
    # image = FileField(u'Фото:', validators=[FileAllowed(['jpeg', 'jpg', 'png'], 'Images only!')])
    image_list = FieldList(FileField(u'Фото:', validators=[FileAllowed(['jpeg', 'jpg', 'png'], 'Images only!')]), min_entries=3)
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


class RecoveryForm(FlaskForm):
    userdata = StringField('Имя пользователя или e-mail', validators=[DataRequired()])
    submit = SubmitField('Подтвердить')

    # Поиск пользователя по имени/e-mail
    @staticmethod
    def find_user_with_data(userdata):
        user = User.query.filter_by(username=userdata).first()
        if user is None:
            user = User.query.filter_by(email=userdata).first()
        return user

# Форма для создания нового пароля
class RecoveryPassForm(FlaskForm):
    password = PasswordField('Пароль', validators=[DataRequired()])
    password2 = PasswordField('Снова пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Подтвердить')

    # Поиск пользователя по recovery word
    @staticmethod
    def find_user_for_recovery(recovery_word):
        user = User.query.filter_by(recovery_word=recovery_word).first()
        if user is None or user.recovery_date < datetime.utcnow():
            return None
        return user
