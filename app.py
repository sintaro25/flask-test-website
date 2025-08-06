from flask import Flask, render_template, url_for, request, flash, session, redirect, abort, g
import sqlite3
import os


DATABASE = '/tmp/flsite.db'
DEBUG = True
SECRET_KEY = 'sdfsdfsdfsdfsd'

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flsite.db')))

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

menu = [
    {'name': 'Главная', 'url': 'index'},
    {'name': 'О нас', 'url': 'about'},
    {'name': 'Контакты', 'url': 'contacts'},
    {'name': 'Оставить отзыв', 'url': 'feedback'}
    ]

@app.route('/')
def index():
    db = get_db()
    return render_template('index.html', menu=menu)

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'link_db'):
        g.link_db.close()

@app.route('/about')
def about():
    return render_template('about_us.html', menu=menu, title='О нас')

@app.route('/portfolio/<int:id>')
def portfolio(id):
    return f"Работа №{id}"

@app.route('/contacts')
def contacts():
    return 'Contacts'

@app.route('/feedback', methods=['POST', 'GET'])
def feedback():
    if request.method == 'POST':
        if len(request.form['username']) > 2:
            flash('Отзыв отправлен', category='success')
        else:
            flash('Ошибка отправки', category='error')
    return render_template('feedback.html', menu=menu)

@app.errorhandler(404)
def pageNotFound(error):
    return render_template('page404.html', menu=menu), 404

@app.route('/login', methods=['POST', 'GET'])
def login():
    if 'userLogged' in session:
        return redirect(url_for('profile', username=session['userLogged']))
    elif request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'admin':
            session['userLogged'] = request.form['username']
            return redirect(url_for('profile', username=session['userLogged']))
        else:
            flash('Неверный логин или пароль', category='error') 
    return render_template('login.html', menu=menu)

@app.route('/profile/<username>')
def profile(username):
    if 'userLogged' not in session or session['userLogged'] != username:
        abort(401)
    return f'Профиль пользователя: {username}'

if __name__ == '__main__':
    app.run(debug=True)