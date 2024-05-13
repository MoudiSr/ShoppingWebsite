from flask import Flask, render_template, redirect, url_for, request, flash, session, abort
from flask_login import LoginManager, current_user, UserMixin, login_user, logout_user
from flask_mysqldb import MySQL
from datetime import date

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)


app.secret_key = 'xdqyM<F|R@I(nx82HWqhSD!1/_=3v4u£:5hD[lS&V6)3;Lw;L\''

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '123456789'
app.config['MYSQL_DB'] = 'deliveryapp'

mysql = MySQL(app)

user = None

class User(UserMixin):
    def __init__(self, id):
        self.id = id
    
    def setUsername(self, username):
        self.username = username
    
    def setPhone(self, phone):
        self.phone = phone

    def setAddress(self, address):
        self.address = address
    
    def setPicture(self, picture):
        self.picture = picture
    
    def setEmail(self, email):
        self.email = email

@login_manager.user_loader
def load_user(user_id):
    con = mysql.connection.cursor()
    con.execute("SELECT * FROM users WHERE id = %s", [user_id])
    userAvail = con.fetchone()
    con.close()

    if userAvail is None:
        return None
    
    user = User(userAvail[0])
    user.setUsername(userAvail[1])
    user.setPhone(userAvail[3])
    user.setAddress(userAvail[4])
    user.setPicture(userAvail[5])
    user.setEmail(userAvail[6])

    return user

@app.route('/')
def index():
    return redirect(url_for('home'))

@app.route('/home')
def home():
    snacks = [
        {'id': 1,'title': 'Pizza Pepperoni', 'price': 5.99, 'img': 'static/img/pepperoni-pizza.jpeg', 'category': 'lunch', 'calories': 2600, 'rating': 4.5, 'type': 'Non Veg', 'numPersons': 3},
        {'id': 2,'title': 'Cheese Burger', 'price': 2.99, 'img': 'static/img/burger.jpg', 'category': 'lunch', 'calories': 350, 'rating': 4.8, 'type': 'Non Veg', 'numPersons': 1},
        {'id': 3,'title': 'Bangin Burger', 'price': 8.49, 'img': 'static/img/Bangin-Breakfast-Burger.jpg', 'category': 'breakfast', 'calories': 800, 'rating': 5, 'type': 'Veg', 'numPersons': 1},
        {'id': 4,'title': 'Egg Pizza', 'price': 6.99, 'img': 'static/img/Breakfast-Pizza.jpg', 'category': 'breakfast', 'calories': 1200, 'rating': 4.7, 'type': 'Non Veg', 'numPersons': 2},
        {'id': 5,'title': 'Strawberry Banana Smoothie', 'price': 1.99, 'img': 'static/img/strawberry-banana-smoothie.jpeg', 'category': 'drinks', 'calories': 2000, 'rating': 4.9, 'type': 'Veg', 'numPersons': 1},
    ]

    return render_template('index.html', snacks=snacks)

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        data = request.get_json()
        session['cart'] = data
        return redirect(url_for('checkout'))
    else:  
        return render_template('checkout.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'POST':
        con = mysql.connection.cursor()
        con.execute("SELECT * FROM users WHERE username = %s", [request.form['username']])
        userAvail = con.fetchone()
        con.close()
        if userAvail is None:
            flash('Account not found!!')
        elif request.form['password'] == userAvail[2]:
            user = User(userAvail[0])

            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Invalid username/password')
    
    return render_template('login.html')

@app.route('/profile')
def profile():
    con = mysql.connection.cursor()
    con.execute("SELECT * FROM orders WHERE uid = %s", [current_user.id])
    orders = con.fetchall()
    orders = [list(order) for order in orders]
    con.close()

    con = mysql.connection.cursor()
    for order in orders:
        con.execute("SELECT name from drivers WHERE id = %s", [order[3]])
        driver = con.fetchone()
        order[3] = driver[0]
    con.close()

    con = mysql.connection.cursor()
    for order in orders:
        con.execute("SELECT * FROM items WHERE oid = %s", [order[0]])
        items = con.fetchall()
        items = [list(item) for item in items]
        order.append(items)
    print(orders)
    con.close()

    return render_template('profile.html', user=current_user, orders=orders, items=items)

@app.route('/profile/update', methods=['POST'])
def updateProfile():
    try:
        username = request.form['username']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']

        con = mysql.connection.cursor()
        con.execute("UPDATE users SET username = %s, email = %s, phone = %s, address = %s WHERE id = %s", (username, email, phone, address, current_user.id))
        mysql.connection.commit()
        con.close()

        flash("Profile updated successfully")

        return redirect(url_for('profile'))
    except Exception as e:
        app.logger.error(f"Error updating profile: {e}")
        abort(500)


@app.route('/profile/changePwd', methods=['POST'])
def changePwd():
    try:
        oldPwd = request.form['old-password']
        newPwd = request.form['new-password']
        confirmPwd = request.form['confirm-password']

        con = mysql.connection.cursor()
        con.execute("SELECT password FROM users WHERE id = %s", [current_user.id])
        user = con.fetchone()
        con.close()

        if oldPwd == user[0] and newPwd == confirmPwd:
            con = mysql.connection.cursor()
            con.execute("UPDATE users SET password = %s WHERE id = %s", [newPwd, current_user.id])
            mysql.connection.commit()
            con.close()

            flash("Password changed successfully")
        elif newPwd != confirmPwd:
            flash("Passwords must match")
        else:
            flash("Invalid old password")

        return redirect(url_for('profile'))
    except Exception as e:
        app.logger.error(f"Error changing password: {e}")
        abort(500)

@app.route('/profile/deleteAccount', methods=['POST'])
def deleteAccount():
    try:
        con = mysql.connection.cursor()
        con.execute("DELETE FROM users WHERE id = %s", [current_user.id])
        mysql.connection.commit()
        con.close()

        flash("Account deleted successfully")

        return redirect(url_for('login'))
    except Exception as e:
        app.logger.error(f"Error deleting account: {e}")
        abort(500)

@app.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/confirm', methods=['POST'])
def checkoutConfirm():
    data = request.get_json()
    if data['message'] == "success":
        con = mysql.connection.cursor()
        con.execute("INSERT INTO orders (date, status, uid, did) VALUES (CURDATE(), %s, %s, %s)", ("Ready", current_user.id, 1))
        con.execute("SELECT LAST_INSERT_ID()")
        order_id = con.fetchone()[0]
        for item in session['cart']:
            con.execute("INSERT INTO items (name, price, quantity, oid) VALUES (%s, %s, %s, %s)", (item['name'], item['price'], item['quantity'], order_id))
        mysql.connection.commit()
        con.close()
        return redirect(url_for('profile'))
    else:
        return redirect(url_for('checkout'))

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)