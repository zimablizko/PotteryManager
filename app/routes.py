import os

from flask import render_template, flash, redirect, url_for, request, send_from_directory
from sqlalchemy import func
from werkzeug.utils import secure_filename

from app import app, db
from app.forms import LoginForm, AddItemForm, MainForm, ListForm
from app.models import Clay, Item, Surface, Glaze, ItemGlaze


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = MainForm()
    if form.validate_on_submit():
        items = Item.query.filter_by(clay_id=form.clay_filter.data).filter_by(surface_id=form.surface_filter.data).all()
    else:
        items = Item.query.all()
    for item in items:
        item.glazes = [g.glaze_id for g in
                       db.session.query(ItemGlaze).filter_by(item_id=item.id).order_by('order').all()]
    return render_template('index.html', form=form, title='Home', glazes=form.glazes, surfaces=form.surfaces,
                           clays=form.clays,
                           items=items)


@app.route('/list', methods=['GET', 'POST'])
def probe_list():
    form = ListForm()
    if form.validate_on_submit():
        print(form.glaze_filter.data)
        items = Item.query
        if form.clay_filter.data:
            items = items.filter(Item.clay_id.in_(form.clay_filter.data))
        if form.surface_filter.data:
            items = items.filter(Item.surface_id.in_(form.surface_filter.data))
        if form.glaze_filter.data:
            items = items.join(ItemGlaze).filter(ItemGlaze.glaze_id.in_(form.glaze_filter.data))
        print(items)
        items = items.all()
    else:
        items = Item.query.all()
    return render_template('list.html', form=form, title='List', glazes=form.glazes, surfaces=form.surfaces,
                           clays=form.clays,
                           items=items)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(form.username.data, form.remember_me.data))
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)


@app.route('/add_item', methods=['GET', 'POST'])
def add_item():
    form = AddItemForm()
    if form.validate_on_submit():
        item = Item(name=form.name.data, description=form.description.data, clay_id=form.clay_id.data,
                    surface_id=form.surface_id.data,
                    temperature=form.temperature.data)
        if form.image.data:
            file = request.files['image']
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            item.image_name = filename
        if not form.name.data:
            item.name = db.session.query(Clay).filter_by(id=item.clay_id).first().name + ' - ' \
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
    return render_template('add_item.html', title='Add new item', form=form)


@app.route('/images/<image>')
def images(image):
    return send_from_directory(app.config['UPLOAD_FOLDER'], image)
