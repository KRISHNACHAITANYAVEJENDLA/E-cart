from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import json

app = Flask(__name__)
app.secret_key = 'secret_key_123'
USERS_FILE = 'users.json'

# ----------------- User Management ------------------

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        users = load_users()

        if email in users:
            flash('User already exists. Please login.', 'warning')
            return redirect(url_for('login'))

        users[email] = password
        save_users(users)
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('registeration.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['username']
        password = request.form['password']
        users = load_users()

        if email not in users:
            flash('User not registered. Please sign up first.', 'danger')
            return redirect(url_for('register'))

        if users[email] == password:
            session['user'] = email
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))

        flash('Incorrect password. Please try again.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('cart', None)
    session.pop('payment_done', None)
    flash('Logged out successfully.', 'info')
    return redirect(url_for('login'))

# ----------------- Product Listings ------------------

products = [
    {"id": 1, "name": "Wireless Headphones", "desc": "Noise-cancelling Bluetooth headphones.", "price": 4000, "img": "images/wirelessheadphones.jpeg"},
    {"id": 2, "name": "Smart Watch", "desc": "Tracks fitness, heart rate, and notifications.", "price": 8999, "img": "images/smart_watch.webp"},
    {"id": 3, "name": "USB-C Cable", "desc": "Fast-charging USB-C cable for Android devices.", "price": 999, "img": "images/usbc.jpeg"},
    {"id": 4, "name": "Laptop Backpack", "desc": "Waterproof backpack fits 15.6\" laptops.", "price": 2999, "img": "images/LaptopBackpack.webp"},
    {"id": 5, "name": "Wireless Mouse", "desc": "Ergonomic mouse with 3 DPI settings.", "price": 1499, "img": "images/wirelessmouse.jpeg"},
    {"id": 6, "name": "Bluetooth Speaker", "desc": "12-hour playtime with deep bass.", "price": 3999, "img": "images/bluetoothspeaker.jpeg"},
    {"id": 7, "name": "LED Desk Lamp", "desc": "Adjustable brightness and color temperature.", "price": 2499, "img": "images/desklamp.jpeg"},
    {"id": 8, "name": "Phone Stand", "desc": "Foldable mobile stand for desk use.", "price": 699, "img": "images/phonestand.jpeg"},
    {"id": 9, "name": "Webcam 1080p", "desc": "Full HD webcam with mic for meetings.", "price": 3499, "img": "images/webcam.jpeg"},
    {"id": 10, "name": "Portable SSD", "desc": "500GB high-speed USB 3.1 SSD.", "price": 7999, "img": "images/portablessd.jpeg"},
    {"id": 11, "name": "Wireless Charger", "desc": "Fast wireless charger for smartphones.", "price": 1999, "img": "images/wirelesscharger.jpeg"},
    {"id": 12, "name": "Gaming Keyboard", "desc": "RGB mechanical keyboard with blue switches.", "price": 2999, "img": "images/gamingkeyboard.jpeg"},
    {"id": 13, "name": "Gaming Mouse", "desc": "Programmable mouse with 7 buttons.", "price": 2599, "img": "images/gamingmouse.jpeg"},
    {"id": 14, "name": "HDMI Cable", "desc": "6ft high-speed HDMI cable for 4K.", "price": 799, "img": "images/hdmicable.jpeg"},
    {"id": 15, "name": "Power Bank", "desc": "10,000mAh charger with dual output.", "price": 2299, "img": "images/powerbank.jpeg"}
]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/products')
def products_page():
    if 'user' not in session:
        flash('Login required to view products.', 'danger')
        return redirect(url_for('login'))
    cart = session.get('cart', [])
    return render_template('productlistings.html', products=products, cart=cart)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if 'user' not in session:
        flash('Login required to add to cart.', 'danger')
        return redirect(url_for('login'))

    product_id = int(request.form.get('product_id'))
    product = next((item for item in products if item['id'] == product_id), None)
    if product:
        cart = session.get('cart', [])
        cart.append(product)
        session['cart'] = cart
        session.modified = True
        flash(f"{product['name']} added to cart!", 'success')
    return redirect(url_for('products_page'))

@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    if 'user' not in session:
        return redirect(url_for('login'))

    index = int(request.form.get('index'))
    cart = session.get('cart', [])
    if 0 <= index < len(cart):
        removed_item = cart.pop(index)
        session['cart'] = cart
        flash(f"{removed_item['name']} removed from cart.", 'info')
    return redirect(url_for('products_page'))

@app.route('/yourorders')
def yourorders():
    if 'user' not in session:
        return redirect(url_for('login'))
    cart = session.get('cart', [])
    return render_template('yourorders.html', cart=cart)

@app.route('/settings')
def settings():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('settings.html')

@app.route('/contactus')
def contactus():
    return render_template('contactus.html')

@app.route('/checkout')
def checkout():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('checkout.html')

@app.route('/payments', methods=['GET', 'POST'])
def payments():
    if 'user' not in session:
        return redirect(url_for('login'))

    cart = session.get('cart', [])
    total_price = sum(item['price'] for item in cart)

    if request.method == 'POST':
        session['payment_done'] = True
        session['cart'] = []
        flash('Payment successful and order placed!', 'success')
        return redirect(url_for('payments'))

    return render_template('payments.html', total_price=total_price)

if __name__ == '__main__':
    app.run(debug=True)
