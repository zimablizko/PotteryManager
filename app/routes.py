import os
from datetime import datetime

from flask import render_template, flash, redirect, url_for, request, send_from_directory
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy import func
from sqlalchemy.sql.functions import count
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from wtforms import SelectField
from wtforms.validators import Optional

from app import app, db
from app.forms import LoginForm, AddItemForm, ListForm, AddGlazeForm, AddClayForm, TableForm, RegistrationForm
from app.models import Clay, Item, Surface, Glaze, ItemGlaze, User


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@app.route('/list', methods=['GET', 'POST'])
@login_required
def index():
    form = ListForm()
    if form.validate_on_submit():
        print(form.glaze_filter.data)
        items = current_user.get_items()
        if form.clay_filter.data > 0:
            items = items.filter(Item.clay_id.__eq__(form.clay_filter.data))
        if form.surface_filter.data > 0:
            items = items.filter(Item.surface_id.__eq__(form.surface_filter.data))
        if form.glaze_filter.data > 0:
            items = items.join(ItemGlaze).filter(ItemGlaze.glaze_id.__eq__(form.glaze_filter.data))
        print(items)
        items = items.all()
    else:
        items = current_user.get_items()
        for item in items:
            print(item.delete_date)
    return render_template('list.html', form=form, title='Все пробники', items=items)


@app.route('/table', methods=['GET', 'POST'])
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
        items = current_user.get_items()
    for item in items:
        item.glazes = [g.glaze_id for g in
                       db.session.query(ItemGlaze).filter_by(item_id=item.id).order_by('order').all()]
    return render_template('index.html', form=form, title='Таблица смешивания', items=items)


@app.route('/add_item', methods=['GET', 'POST'])
def add_item():
    form = AddItemForm(None)
    if form.validate_on_submit():
        item = Item(name=form.name.data, description=form.description.data, clay_id=form.clay_id.data,
                    surface_id=form.surface_id.data, user_id=current_user.id,
                    temperature=form.temperature.data)
        if form.image.data:
            file = request.files['image']
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            item.image_name = filename
        if not form.name.data:
            item.name = db.session.query(Clay).filter_by(id=item.clay_id).first().name + ': ' \
                        + db.session.query(Glaze).filter_by(id=form.glaze_id_1.data).first().name
        max_id = db.session.query(func.max(Item.id)).scalar() + 1
        item_glaze = ItemGlaze(glaze_id=form.glaze_id_1.data, item_id=max_id, order=0)
        db.session.add(item_glaze)
        if form.glaze_id_2.data > 0:
            item_glaze_2 = ItemGlaze(glaze_id=form.glaze_id_2.data, item_id=max_id, order=1)
            db.session.add(item_glaze_2)
            if not form.name.data:
                item.name += ' + ' + db.session.query(Glaze).filter_by(id=form.glaze_id_2.data).first().name
        if form.glaze_id_3.data > 0:
            item_glaze_3 = ItemGlaze(glaze_id=form.glaze_id_3.data, item_id=max_id, order=2)
            db.session.add(item_glaze_3)
            if not form.name.data:
                item.name += ' + ' + db.session.query(Glaze).filter_by(id=form.glaze_id_3.data).first().name
        db.session.add(item)
        db.session.commit()
        flash('Item {} added!'.format(form.name.data))
        return redirect(url_for('index'))
    return render_template('add_item.html', title='Добавление пробника', form=form)


@app.route('/edit_item/<item_id>', methods=['GET', 'POST'])
def edit_item(item_id):
    form = AddItemForm(item_id)
    if form.validate_on_submit():
        print("EDIT")
        item = db.session.query(Item).filter(Item.id == item_id).one()
        if not form.name.data:
            item.name = db.session.query(Clay).filter_by(id=item.clay_id).first().name + ': ' \
                        + db.session.query(Glaze).filter_by(id=form.glaze_id_1.data).first().name
        else:
            item.name = form.name.data
        item_glaze_1 = db.session.query(ItemGlaze).filter(ItemGlaze.item_id == item_id).filter(
            ItemGlaze.order == 0).one_or_none()
        item_glaze_1.glaze_id = form.glaze_id_1.data
        if form.glaze_id_2.data > 0:
            item_glaze_2 = db.session.query(ItemGlaze).filter(ItemGlaze.item_id == item_id).filter(
                ItemGlaze.order == 1).one_or_none()
            if item_glaze_2:
                item_glaze_2.glaze_id = form.glaze_id_2.data
            else:
                item_glaze_2 = ItemGlaze(glaze_id=form.glaze_id_2.data, item_id=item_id, order=1)
                db.session.add(item_glaze_2)
            if not form.name.data:
                item.name += ' + ' + db.session.query(Glaze).filter_by(id=form.glaze_id_2.data).first().name
        if form.glaze_id_3.data > 0:
            item_glaze_3 = db.session.query(ItemGlaze).filter(ItemGlaze.item_id == item_id).filter(
                ItemGlaze.order == 2).one_or_none()
            if item_glaze_3:
                item_glaze_3.glaze_id = form.glaze_id_3.data
            else:
                item_glaze_3 = ItemGlaze(glaze_id=form.glaze_id_3.data, item_id=item_id, order=2)
                db.session.add(item_glaze_3)
            if not form.name.data:
                item.name += ' + ' + db.session.query(Glaze).filter_by(id=form.glaze_id_3.data).first().name
        item.description = form.description.data
        item.temperature = form.temperature.data
        item.clay_id = form.clay_id.data
        item.surface_id = form.surface_id.data
        if form.image.data:
            file = request.files['image']
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            item.image_name = filename
        print(form.name.data)
        print(item)
        db.session.commit()
        return redirect(url_for('index'))
    elif request.method == 'GET':
        print("INIT  " + str(item_id))
        item = Item.query.filter_by(id=item_id).one()
        form.id = item.id
        glaze_1 = ItemGlaze.query.filter_by(item_id=item.id).filter_by(order=0).order_by('order').one_or_none()
        glaze_2 = ItemGlaze.query.filter_by(item_id=item.id).filter_by(order=1).order_by('order').one_or_none()
        glaze_3 = ItemGlaze.query.filter_by(item_id=item.id).filter_by(order=2).order_by('order').one_or_none()
        form.name.data = item.name
        form.description.data = item.description
        form.temperature.data = item.temperature
        if glaze_1:
            form.glaze_id_1.data = glaze_1.glaze_id
        if glaze_2:
            form.glaze_id_2.data = glaze_2.glaze_id
        if glaze_3:
            form.glaze_id_3.data = glaze_3.glaze_id
        form.clay_id.data = item.clay_id
        form.surface_id.data = item.surface_id
        form.image.data = item.image_name
        form.submit.label.text = 'Изменить'
    return render_template('add_item.html', title='Изменение пробника', form=form)


@app.route('/delete_item/<item_id>', methods=['GET', 'POST'])
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
    return redirect(url_for('index'))


@app.route('/add_glaze', methods=['GET', 'POST'])
def add_glaze():
    form = AddGlazeForm()
    if form.validate_on_submit():
        glaze = Glaze(name=form.name.data, user_id=current_user.id)
        db.session.add(glaze)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_glaze.html', title='Добавление глазури', form=form)


@app.route('/add_clay', methods=['GET', 'POST'])
def add_clay():
    form = AddClayForm()
    if form.validate_on_submit():
        clay = Clay(name=form.name.data, user_id=current_user.id)
        db.session.add(clay)
        db.session.commit()
        return redirect(url_for('index'))
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
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


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
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

# ----------- OTHER STUFF ----------- #
@app.route('/images/<image>')
def images(image):
    return send_from_directory(app.config['UPLOAD_FOLDER'], image)
