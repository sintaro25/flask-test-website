from flask import Flask, render_template, url_for, request, flash, session, redirect, abort, g
import sqlite3
import os
from db_class import FDataBase


DATABASE = '/tmp/flsite.db'
DEBUG = True
SECRET_KEY = 'sdfsdfsdfsdfsd'
UPLOAD_FOLDER = 'static/images/'

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flsite.db')))
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def create_db():
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()

def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'link_db'):
        g.link_db.close()

@app.route('/')
def index():
    db = get_db()
    dbase = FDataBase(db)
    return render_template('index.html', menu = dbase.getMenu())

@app.route('/about')
def about():
    db = get_db()
    dbase = FDataBase(db)
    return render_template('about_us.html', menu=dbase.getMenu(), title='О нас')

@app.route('/portfolio', methods=['POST', 'GET'])
def portfolio():
    db = get_db()
    dbase = FDataBase(db)
    
    if request.method == 'POST':
        res = dbase.addImage(app, request.files['image'])
        if not res:
            flash('Ошибка добавления изображения', category = 'error')
        else:
            flash('Изображение успешно добавлено', category = 'success')
    
    return render_template('portfolio.html', menu=dbase.getMenu(), images=dbase.getImages())

@app.route('/contacts')
def contacts():
    return 'Contacts'

@app.route('/feedback', methods=['POST', 'GET'])
def feedback():
    db = get_db()
    dbase = FDataBase(db)
    if request.method == 'POST':
        if len(request.form['username']) > 2:
            flash('Отзыв отправлен', category='success')
        else:
            flash('Ошибка отправки', category='error')
    return render_template('feedback.html', menu=dbase.getMenu())

@app.errorhandler(404)
def pageNotFound(error):
    db = get_db()
    dbase = FDataBase(db)
    return render_template('page404.html', menu=dbase.getMenu()), 404

@app.route('/login', methods=['POST', 'GET'])
def login():
    db = get_db()
    dbase = FDataBase(db)
    if 'userLogged' in session:
        return redirect(url_for('profile', username=session['userLogged']))
    elif request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'admin':
            session['userLogged'] = request.form['username']
            return redirect(url_for('profile', username=session['userLogged']))
        else:
            flash('Неверный логин или пароль', category='error') 
    return render_template('login.html', menu=dbase.getMenu())

@app.route('/profile/<username>')
def profile(username):
    if 'userLogged' not in session or session['userLogged'] != username:
        abort(401)
    return f'Профиль пользователя: {username}'

if __name__ == '__main__':
    app.run(debug=True)