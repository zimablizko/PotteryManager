import os
import random
import string

from datetime import datetime

from flask import render_template, flash, redirect, url_for, request, send_from_directory
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy import func
from sqlalchemy.sql.functions import count
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from wtforms import SelectField
from wtforms.validators import Optional

from app import app, db, utils
from app.forms import LoginForm, AddItemForm, ListForm, AddGlazeForm, AddClayForm, TableForm, RegistrationForm, \
    ItemForm, RecoveryForm, RecoveryPassForm, ItemsForm
from app.models import Clay, Item, Surface, Glaze, ItemGlaze, User, ItemImage, Image


@app.route('/list', methods=['GET', 'POST'])
@app.route('/list/<int:page>', methods=['GET', 'POST'])
@login_required
def list(page=1):
    form = ListForm()
    if form.validate_on_submit():
        items = current_user.get_items()
        if form.clay_filter.data > 0:
            items = items.filter(Item.clay_id.__eq__(form.clay_filter.data))
        if form.surface_filter.data > 0:
            items = items.filter(Item.surface_id.__eq__(form.surface_filter.data))
        if form.glaze_filter.data > 0:
            items = items.join(ItemGlaze).filter(ItemGlaze.glaze_id.__eq__(form.glaze_filter.data))
        items = items.paginate(page, app.config['ITEMS_PER_PAGE'], False)
    else:
        items = current_user.get_items().paginate(page, app.config['ITEMS_PER_PAGE'], False)
    return render_template('list.html', form=form, title='Мои пробники', items=items)


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@app.route('/index/<int:page>', methods=['GET', 'POST'])
@app.route('/items', methods=['GET', 'POST'])
@app.route('/items/<int:page>', methods=['GET', 'POST'])
def index(page=1):
    form = ItemsForm()
    public_items = form.get_public_items().paginate(page, app.config['ITEMS_PER_PAGE'], False)
    return render_template('items.html', form=form, title='Публичные пробники', items=public_items)


@app.route('/table', methods=['GET', 'POST'])
@login_required
def table():
    form = TableForm()
    if form.validate_on_submit():
        items = current_user.get_items()
        if form.clay_filter.data > 0:
            items = items.filter(Item.clay_id.__eq__(form.clay_filter.data))
        if form.surface_filter.data > 0:
            items = items.filter(Item.surface_id.__eq__(form.surface_filter.data))
        items = items.all()
    else:
        items = current_user.get_items().all()
    for item in items:
        item.glazes = [g.glaze_id for g in
                       db.session.query(ItemGlaze).filter_by(item_id=item.id).order_by('order').all()]
    return render_template('table.html', form=form, title='Таблица смешивания', items=items)


@app.route('/item/<item_id>', methods=['GET', 'POST'])
def item(item_id):
    form = ItemForm(item_id)
    item = db.session.query(Item).filter(Item.id == item_id).one()
    if not item.is_public and (current_user.is_anonymous or current_user.id != item.user_id):
        return render_template('error.html', error="Ошибка доступа")
    return render_template('item.html', form=form, item=item)


@app.route('/add_item', methods=['GET', 'POST'])
@login_required
def add_item():
    form = AddItemForm(None)
    form.image_names = [None] * 3
    if form.validate_on_submit():
        item = Item(name=form.name.data, description=form.description.data, clay_id=form.clay_id.data,
                    surface_id=form.surface_id.data, user_id=current_user.id,
                    temperature=form.temperature.data, is_public=form.is_public.data)
        #if form.image.data:
        #    utils.save_image(request.files['image'], item)
        if not form.name.data:
            item.name = db.session.query(Clay).filter_by(id=item.clay_id).first().name + ': ' \
                        + db.session.query(Glaze).filter_by(id=form.glaze_list[0].data).first().name
        db.session.add(item)
        item_id = db.session.query(func.max(Item.id)).scalar()
        # Обработка глазурей
        for i, item_glaze in enumerate([None] * app.config['GLAZE_MAX_COUNT']):
            item_glaze = db.session.query(ItemGlaze).filter(ItemGlaze.item_id == item_id).filter(
                ItemGlaze.order == i).one_or_none()
            if form.glaze_list[i].data > 0:
                if item_glaze:
                    item_glaze.glaze_id = form.glaze_list[i].data
                else:
                    item_glaze = ItemGlaze(glaze_id=form.glaze_list[i].data, item_id=item_id, order=i)
                    db.session.add(item_glaze)
                if not form.name.data:
                    item.name += ' + ' + db.session.query(Glaze).filter_by(id=form.glaze_list[i].data).first().name
            else:
                if item_glaze:
                    db.session.delete(item_glaze)
        # Обработка изображений
        for i, item_image in enumerate([None] * app.config['IMAGE_MAX_COUNT']):
            item_image = db.session.query(ItemImage).filter(ItemImage.item_id == item_id).filter(
                ItemImage.order == i).one_or_none()
            if form.image_list[i].data:
                image = Image()
                utils.save_image(request.files['image_list-'+str(i)], image)
                db.session.add(image)
                image_id = db.session.query(func.max(Image.id)).scalar()
                if item_image:
                    item_image.image_id = image_id
                else:
                    item_image = ItemImage(image_id=image_id, item_id=item_id, order=i)
                    db.session.add(item_image)
        flash('Пробник {} добавлен!'.format(item.name))
        db.session.commit()
        return redirect(url_for('list'))
    return render_template('add_item.html', title='Добавление пробника', form=form)


@app.route('/edit_item/<item_id>', methods=['GET', 'POST'])
@login_required
def edit_item(item_id):
    form = AddItemForm(item_id)
    if form.validate_on_submit():
        # Сохранение полей пробника
        item = db.session.query(Item).filter(Item.id == item_id).one()
        if not form.name.data:
            item.name = db.session.query(Clay).filter_by(id=item.clay_id).first().name + ': ' \
                        + db.session.query(Glaze).filter_by(id=form.glaze_list[0].data).first().name
        else:
            item.name = form.name.data
        item.description = form.description.data
        item.temperature = form.temperature.data
        item.clay_id = form.clay_id.data
        item.surface_id = form.surface_id.data
        item.is_public = form.is_public.data
        item.edit_date = datetime.utcnow()
       # if form.image.data:
        #    utils.save_image(request.files['image'], item)
        # Обработка глазурей
        for i, item_glaze in enumerate([None] * app.config['GLAZE_MAX_COUNT']):
            item_glaze = db.session.query(ItemGlaze).filter(ItemGlaze.item_id == item_id).filter(
                ItemGlaze.order == i).one_or_none()
            if form.glaze_list[i].data > 0:
                if item_glaze:
                    item_glaze.glaze_id = form.glaze_list[i].data
                else:
                    item_glaze = ItemGlaze(glaze_id=form.glaze_list[i].data, item_id=item_id, order=i)
                    db.session.add(item_glaze)
                if not form.name.data:
                    item.name += ' + ' + db.session.query(Glaze).filter_by(id=form.glaze_list[i].data).first().name
            else:
                if item_glaze:
                    db.session.delete(item_glaze)
        # Обработка изображений
        print("tetetet")
        print(form.image_list)
        for i, item_image in enumerate([None] * app.config['IMAGE_MAX_COUNT']):
            item_image = db.session.query(ItemImage).filter(ItemImage.item_id == item_id).filter(
                ItemImage.order == i).one_or_none()
            if form.image_list[i].data:
                print(form.image_list[i].data)
                image = Image()
                utils.save_image(request.files['image_list-' + str(i)], image)
                db.session.add(image)
                image_id = db.session.query(func.max(Image.id)).scalar()
                if item_image:
                    item_image.image_id = image_id
                else:
                    item_image = ItemImage(image_id=image_id, item_id=item_id, order=i)
                    db.session.add(item_image)
        db.session.commit()
        return redirect(url_for('list'))
    elif request.method == 'GET':
        item = Item.query.filter_by(id=item_id).one()
        form.id = item.id
        glaze_list = [None] * 3
        for i, glaze in enumerate(glaze_list):
            glaze = ItemGlaze.query.filter_by(item_id=item.id).filter_by(order=i).one_or_none()
            if glaze:
                form.glaze_list[i].data = glaze.glaze_id
        form.image_names = [None] * 3
        for i, image in enumerate(form.image_names):
            item_image = ItemImage.query.filter_by(item_id=item.id).filter_by(order=i).one_or_none()
            if item_image:
                image = Image.query.filter_by(id=item_image.image_id).one_or_none()
                if image:
                    form.image_names[i] = image.name
        form.name.data = item.name
        form.description.data = item.description
        form.temperature.data = item.temperature
        form.is_public.data = item.is_public
        form.clay_id.data = item.clay_id
        form.surface_id.data = item.surface_id
        #form.image_name = item.image_name
        form.submit.label.text = 'Изменить'
    return render_template('add_item.html', title='Изменение пробника', form=form)


@app.route('/delete_item/<item_id>', methods=['GET', 'POST'])
@login_required
def delete_item(item_id):
    item = db.session.query(Item).filter(Item.id == item_id).one()
    if item:
        # item_glazes = db.session.query(ItemGlaze).filter(ItemGlaze.item_id == item_id).all()
        # if len(item_glazes) > 0:
        #     for item_glaze in item_glazes:
        #         db.session.delete(item_glaze)
        # db.session.delete(item)
        item.delete_date = datetime.utcnow()
        db.session.commit()
    return redirect(url_for('list'))


@app.route('/add_glaze', methods=['GET', 'POST'])
@login_required
def add_glaze():
    form = AddGlazeForm()
    if form.validate_on_submit():
        glaze = Glaze(name=form.name.data, user_id=current_user.id)
        db.session.add(glaze)
        db.session.commit()
        return redirect(url_for('list'))
    return render_template('add_glaze.html', title='Добавление глазури', form=form)


@app.route('/add_clay', methods=['GET', 'POST'])
@login_required
def add_clay():
    form = AddClayForm()
    if form.validate_on_submit():
        clay = Clay(name=form.name.data, user_id=current_user.id)
        db.session.add(clay)
        db.session.commit()
        return redirect(url_for('list'))
    return render_template('add_clay.html', title='Добавление глины', form=form)


# ----------- USER STUFF ----------- #
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Неверное имя пользователя или пароль')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Вход', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Добро пожаловать на My Glazes!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/recovery', methods=['GET', 'POST'])
def recovery():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RecoveryForm()
    form.recovery_flag = False
    if form.validate_on_submit():
        user = form.find_user_with_data(form.userdata.data)
        if user is None:
            flash('Такое имя пользователя или e-mail в системе не найдены')
            return redirect(url_for('recovery'))
        recovery_word = user.set_recovery_word()
        db.session.commit()
        utils.send_recovery_email(user.email, recovery_word)
        flash('Ссылка на сброс пароля отправлена по e-mail')
        return redirect(url_for('login'))
    return render_template('recovery.html', title='Восстановление доступа', form=form)


@app.route('/recovery/<recovery_word>', methods=['GET', 'POST'])
def recovery_pass(recovery_word):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RecoveryPassForm()
    user = form.find_user_for_recovery(recovery_word)
    if user is None:
        flash('Ссылка на восстановление недействительна')
        return redirect(url_for('login'))
    form.recovery_flag = True
    if form.validate_on_submit():
        user.set_password(form.password.data)
        user.recovery_date = datetime.utcnow()
        db.session.commit()
        flash('Пароль изменен')
        return redirect(url_for('login'))
    return render_template('recovery.html', title='Восстановление доступа', form=form)


# ----------- OTHER STUFF ----------- #
@app.route('/images/<image>')
def images(image):
    return send_from_directory(app.config['IMAGE_FOLDER'], image)


@app.route('/thumbnails/<image>')
def thumbnails(image):
    return send_from_directory(app.config['THUMBNAIL_FOLDER'], image)


@app.route('/about', methods=['GET', 'POST'])
@login_required
def about():
    return render_template('about.html', title='О проекте')
