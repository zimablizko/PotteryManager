import os

from flask import render_template, flash, redirect, url_for, request, send_from_directory
from werkzeug.utils import secure_filename

from app import app, db
from app.forms import LoginForm, AddItemForm, MainForm
from app.models import Clay, Item, Surface, Glaze


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = MainForm()
    if form.validate_on_submit():
        print("LUL")
        items = Item.query.filter_by(clay_id=form.clay_filter.data).filter_by(surface_id=form.surface_filter.data).all()
    else:
        print("NOTLUL")
        items = Item.query.all()
    return render_template('index.html', form=form, title='Home', glazes=form.glazes, surfaces=form.surfaces, clays=form.clays,
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
        item = Item(name=form.name.data, clay_id=form.clay_id.data, surface_id=form.surface_id.data,
                    glaze_id_1=form.glaze_id_1.data, glaze_id_2=form.glaze_id_2.data)
        if form.image.data:
            file = request.files['image']
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            item.image_name = filename
        db.session.add(item)
        db.session.commit()
        flash('Item {} added!'.format(form.name.data))
        return redirect(url_for('index'))
    return render_template('add_item.html', title='Add new item', form=form)


@app.route('/images/<image>')
def images(image):
    return send_from_directory(app.config['UPLOAD_FOLDER'], image)
