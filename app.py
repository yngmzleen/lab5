from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
from psycopg2.extras import RealDictCursor
import os

app = Flask(__name__)
app.secret_key = 'secret'

# Настройки подключения к PostgreSQL
DB_HOST = os.getenv('DB_HOST', '...')
DB_PORT = os.getenv('DB_PORT', '...')
DB_NAME = os.getenv('DB_NAME', '...')
DB_USER = os.getenv('DB_USER', '...')
DB_PASSWORD = os.getenv('DB_PASSWORD', '...')

# Функция для подключения к базе данных
def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    return conn

# Настройка flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Модель пользователя
class User(UserMixin):
    def __init__(self, id, email, password, name):
        self.id = id
        self.email = email
        self.password = password
        self.name = name

# Загрузка пользователя
@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT * FROM users WHERE id = %s', (user_id,))
    user_data = cur.fetchone()
    cur.close()
    conn.close()
    
    if user_data:
        return User(user_data['id'], user_data['email'], user_data['password'], user_data['name'])
    return None

# GET / - Корневая страница
@app.route('/')
@login_required
def index():
    return render_template('index.html', user=current_user)

# GET /login - Страница входа
@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')

# POST /login - Обработка входа
@app.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    
    # Поиск пользователя по email
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT * FROM users WHERE email = %s', (email,))
    user_data = cur.fetchone()
    cur.close()
    conn.close()
    
    # Проверка существования пользователя
    if not user_data:
        flash('Пользователь не найден')
        return redirect(url_for('login'))
    
    # Проверка пароля
    if not check_password_hash(user_data['password'], password):
        flash('Неверный пароль')
        return redirect(url_for('login'))
    
    # Авторизация пользователя
    user = User(user_data['id'], user_data['email'], user_data['password'], user_data['name'])
    login_user(user)
    
    return redirect(url_for('index'))

# GET /signup - Страница регистрации
@app.route('/signup', methods=['GET'])
def signup():
    return render_template('signup.html')

# POST /signup - Обработка регистрации
@app.route('/signup', methods=['POST'])
def signup_post():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    
    # Проверка существования пользователя
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT * FROM users WHERE email = %s', (email,))
    user_data = cur.fetchone()
    
    if user_data:
        cur.close()
        conn.close()
        flash('Пользователь с таким email уже существует')
        return redirect(url_for('signup'))
    
    # Создание нового пользователя
    hashed_password = generate_password_hash(password)
    cur.execute('INSERT INTO users (email, password, name) VALUES (%s, %s, %s)',
                (email, hashed_password, name))
    conn.commit()
    cur.close()
    conn.close()
    
    return redirect(url_for('login'))

# GET /logout - Выход
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)

