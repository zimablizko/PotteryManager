import os

from flask import render_template, flash, redirect, url_for, request, send_from_directory
from werkzeug.utils import secure_filename

from app import app, db
from app.forms import LoginForm, AddItemForm
from app.models import Clay, Item


@app.route('/')
@app.route('/index')
def index():
    items = Item.query.all()
    clays = Clay.query.all()
    return render_template('index.html', title='Home', clays=clays, items=items)


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
        item = Item(name=form.name.data, clay_id_1=form.clay_id_1.data, clay_id_2=form.clay_id_2.data)
        if form.picture.data:
            file = request.files['picture']
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            item.picture = filename
        db.session.add(item)
        db.session.commit()
        flash('Item added!')
        return redirect(url_for('index'))
    return render_template('add_item.html', title='Add new item', form=form)


@app.route('/images/<image>')
def images(image):
    return send_from_directory(app.config['UPLOAD_FOLDER'], image)
