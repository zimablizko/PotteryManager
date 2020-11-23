from datetime import datetime

from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileRequired
from sqlalchemy import select, desc
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, FileField, RadioField, \
    IntegerField, TextAreaField, SelectMultipleField, FieldList, MultipleFileField
from wtforms.fields.html5 import IntegerRangeField
from wtforms.validators import DataRequired, ValidationError, Optional, length, EqualTo, Email

from app.models import Item, ItemGlaze, User, Material


class ItemsForm(FlaskForm):
    def __init__(self, *args, **kwargs):
        super(ItemsForm, self).__init__(*args, **kwargs)
        glazes_choices = [(c.id, c.name) for c in Material.query.filter_by(type_id=1).filter(Material.delete_date == None).order_by('id')]
        clays_choices = ([(0, 'Все')]).__add__([(c.id, c.name) for c in Material.query.filter_by(type_id=2).filter(Material.delete_date == None).order_by('id')])
        self.glaze_filter.choices = glazes_choices
        self.clay_filter.choices = clays_choices
    glaze_filter = SelectMultipleField('Глазурь:', choices=None, coerce=int, validators=[Optional()], render_kw={'data-live-search':'true'})
    clay_filter = SelectField('Глина:', choices=None, validators=[Optional()])
    temperature_min_filter = IntegerField('Температура:', validators=[Optional()])
    temperature_max_filter = IntegerField('Температура:', validators=[Optional()])
    submit = SubmitField('Фильтр')

    def get_public_items(self):
        return Item.query.filter(Item.delete_date == None).filter(Item.is_public == True).order_by(desc(Item.edit_date))

class ListForm(FlaskForm):
    def __init__(self, *args, **kwargs):
        super(ListForm, self).__init__(*args, **kwargs)
        glazes_choices = [(c.id, c.name) for c in current_user.get_materials(1)]
        clays_choices = ([(0, 'Все')]).__add__([(c.id, c.name) for c in current_user.get_materials(2)])
        self.glaze_filter.choices = glazes_choices
        self.clay_filter.choices = clays_choices
    glaze_filter = SelectMultipleField('Глазурь:', choices=None, coerce=int, validators=[Optional()], render_kw={'data-live-search':'true'})
    clay_filter = SelectField('Глина:', choices=None, validators=[Optional()])
    temperature_min_filter = IntegerField('Температура:', validators=[Optional()])
    temperature_max_filter = IntegerField('Температура:', validators=[Optional()])
    submit = SubmitField('Фильтр')


class TableForm(FlaskForm):
    def __init__(self, *args, **kwargs):
        super(TableForm, self).__init__(*args, **kwargs)
        glazes = current_user.get_materials(1)
        glazes_choices = [(c.id, c.name) for c in glazes]
        clays_choices = ([(0, 'Все')]).__add__([(c.id, c.name) for c in current_user.get_materials(2)])
        self.glazes = glazes
        self.glaze_filter.choices = glazes_choices
        self.clay_filter.choices = clays_choices

    glazes = None
    #glaze_filter = SelectField('Глазурь:', choices=None, coerce=int, validators=[Optional()])
    glaze_filter = SelectMultipleField('Глазурь:', choices=None, coerce=int, validators=[Optional()], render_kw={'data-live-search':'true'})
    clay_filter = SelectField('Глина:', choices=None, coerce=int, validators=[Optional()])
    temperature_min_filter = IntegerField('Температура:', validators=[Optional()])
    temperature_max_filter = IntegerField('Температура:', validators=[Optional()])
    submit = SubmitField('Фильтр')


class ItemForm(FlaskForm):
    submit = SubmitField('Фильтр')


class AddItemForm(FlaskForm):
    def __init__(self, item_id, *args, **kwargs):
        super(AddItemForm, self).__init__(*args, **kwargs)
        glazes_choices = [(c.id, c.name) for c in current_user.get_materials(1)]
        glazes_additional_choices = ([(0, '_нет_')]).__add__(glazes_choices)
        clays_choices = [(c.id, c.name) for c in current_user.get_materials(2)]
        self.glaze_list[0].choices = glazes_choices
        self.glaze_list[1].choices = glazes_additional_choices
        self.glaze_list[2].choices = glazes_additional_choices
        self.clay_id.choices = clays_choices
        self.glaze_list[0].label = "Глазурь 1:"
        self.glaze_list[1].label = "Глазурь 2:"
        self.glaze_list[2].label = "Глазурь 3:"

    name = StringField('Название пробника:', validators=[Optional(), length(max=256)])
    description = TextAreaField('Описание:', validators=[Optional(), length(max=500)])
    is_public = BooleanField('Публичный доступ:')
    temperature = IntegerField('Температура:', validators=[DataRequired()])
    glaze_list = FieldList(SelectField('', choices=None, validate_choice=False,
                             coerce=int), min_entries=3)
    clay_id = SelectField('Глина:', choices=None, validate_choice=False, coerce=int)
    # image = FileField(u'Фото:', validators=[FileAllowed(['jpeg', 'jpg', 'png'], 'Images only!')])
    image_list = FieldList(FileField(u'Фото:', validators=[FileAllowed(['jpeg', 'jpg', 'png'], 'Images only!')]), min_entries=3)
    images = MultipleFileField(u'Фото:', validators=[FileAllowed(['jpeg', 'jpg', 'png'], 'Images only!')])
    submit = SubmitField('Готово')


class AddMaterialForm(FlaskForm):
    def __init__(self, *args, **kwargs):
        super(AddMaterialForm, self).__init__(*args, **kwargs)
        type_choices = [(c.id, c.name) for c in current_user.get_material_types()]
        self.type_id.choices = type_choices

    name = StringField('Название материала:', validators=[Optional(), length(max=256)])
    type_id = SelectField('Тип материала:', choices=None, validate_choice=False, coerce=int)
    submit = SubmitField('Готово')


class MaterialListForm(FlaskForm):
    submit = SubmitField('Фильтр')


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
