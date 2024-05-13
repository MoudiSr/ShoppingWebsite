from app import app
from flask_login import current_user

@app.route('/')
def index():
    return redirect(url_for('home'))

@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/checkout')
def checkout():
    return render_template('checkout.html')

@app.route('/login')
def login():
    return render_template('login.html')


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404