from flask import Flask, render_template, url_for, request, flash, session, redirect, abort, g
import sqlite3
import os
from db_class import FDataBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager


DATABASE = '/tmp/flsite.db'
DEBUG = True
SECRET_KEY = 'sdfsdfsdfsdfsd'
UPLOAD_FOLDER = 'static/images/'

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flsite.db')))
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

login_manager = LoginManager(app)

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

dbase = None

@app.before_request
def before_request():
    global dbase 
    db = get_db()
    dbase = FDataBase(db)

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'link_db'):
        g.link_db.close()

@app.route('/')
def index():
    return render_template('index.html', menu = dbase.getMenu())

@app.route('/about')
def about():
    return render_template('about_us.html', menu=dbase.getMenu(), title='О нас')

@app.route('/portfolio', methods=['POST', 'GET'])
def portfolio():
    if request.method == 'POST':
        res = dbase.addImage(app, request.files['image'])
        if not res:
            flash('Ошибка добавления изображения', category = 'error')
        else:
            flash('Изображение успешно добавлено', category = 'success')
    
    return render_template('portfolio.html', menu=dbase.getMenu(), images=dbase.getImages())

@app.route('/feedback', methods=['POST', 'GET'])
def feedback():
    if request.method == 'POST':
        if len(request.form['username']) > 2:
            flash('Отзыв отправлен', category='success')
        else:
            flash('Ошибка отправки', category='error')
    return render_template('feedback.html', menu=dbase.getMenu())

@app.errorhandler(404)
def pageNotFound(error):
    return render_template('page404.html', menu=dbase.getMenu()), 404

@app.route('/login', methods=['POST', 'GET'])
def login():
    if 'userLogged' in session:
        return redirect(url_for('profile', username=session['userLogged']))
    elif request.method == 'POST':
        if request.form['email'] == 'admin' and request.form['psw'] == 'admin':
            session['userLogged'] = request.form['email']
            return redirect(url_for('profile', username=session['userLogged']))
        else:
            flash('Неверный логин или пароль', category='error') 
    return render_template('login.html', menu=dbase.getMenu())

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        if len(request.form['name']) > 4 and len(request.form['email']) > 4 and \
        len(request.form['psw']) > 4 and request.form['psw'] == request.form['psw2']:
            hash = generate_password_hash(request.form['psw'])
            res = dbase.addUser(request.form['name'], request.form['email'], hash)
            if res:
                flash('Вы успешно зарегистрированы', category='success')
                return redirect(url_for('login'))
            else:
                flash('Ошибка регистрации, попробуйте еще раз', category='error')
        else:
            flash('Неверно заполнены поля', category='error')

    return render_template('register.html', menu=dbase.getMenu())

@app.route('/profile/<username>')
def profile(username):
    if 'userLogged' not in session or session['userLogged'] != username:
        abort(401)
    return f'Профиль пользователя: {username}'

if __name__ == '__main__':
    app.run(debug=True)