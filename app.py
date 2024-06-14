from flask import Flask, render_template, request, redirect, url_for, flash, session
import requests

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Untuk Flash Messages dan Session

API_URL = 'http://127.0.0.1:5500'  # URL dari REST API

# Route untuk halaman register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            response = requests.post(API_URL + '/register', json={'username': username, 'password': password})
            if response.status_code == 200:
                flash('Registration successful. Please login.', 'success')
                return redirect(url_for('login'))
            else:
                flash('Registration failed. Try a different username.', 'error')
        except requests.exceptions.RequestException as e:
            flash(f'Error: {e}', 'error')
    return render_template('register.html')

# Route untuk halaman login
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            response = requests.post(API_URL + '/login', json={'username': username, 'password': password})
            if response.status_code == 200:
                session['username'] = username
                session['password'] = password
                return redirect(url_for('products'))
            else:
                flash('Login failed. Check your credentials and try again.', 'error')
        except requests.exceptions.RequestException as e:
            flash(f'Error: {e}', 'error')
    return render_template('login.html')

# Route untuk halaman produk
@app.route('/products')
def products():
    if 'username' not in session:
        return redirect(url_for('login'))
    try:
        response = requests.get(API_URL + '/products')
        products = response.json()
        return render_template('products.html', products=products)
    except requests.exceptions.RequestException as e:
        flash(f'Error fetching data from API: {e}', 'error')
        return render_template('products.html', products=[])

# Route untuk menambahkan Product baru
@app.route('/add_product', methods=['POST'])
def add_product():
    if 'username' not in session:
        return redirect(url_for('login'))
    try:
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        response = requests.post(API_URL + '/product', json={
            'name': name,
            'description': description,
            'price': price
        })
        if response.status_code == 200:
            flash('Product added successfully', 'success')
        else:
            flash('Failed to add product', 'error')
    except requests.exceptions.RequestException as e:
        flash(f'Error: {e}', 'error')
    return redirect(url_for('products'))

# Route untuk menghapus Product berdasarkan ID
@app.route('/delete_product/<int:id>', methods=['POST'])
def delete_product(id):
    if 'username' not in session:
        return redirect(url_for('login'))
    try:
        response = requests.delete(API_URL + '/product/' + str(id))
        if response.status_code == 200:
            flash('Product deleted successfully', 'success')
        else:
            flash('Failed to delete product', 'error')
    except requests.exceptions.RequestException as e:
        flash(f'Error: {e}', 'error')
    return redirect(url_for('products'))

# Route untuk update product
@app.route('/update_product/<int:id>', methods=['GET', 'POST'])
def update_product(id):
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        try:
            name = request.form['name']
            description = request.form['description']
            price = request.form['price']
            response = requests.put(API_URL + '/product/' + str(id), json={
                'name': name,
                'description': description,
                'price': price
            })
            if response.status_code == 200:
                flash('Product updated successfully', 'success')
            elif response.status_code == 404:
                flash('Product not found', 'error')
            else:
                flash('Failed to update product', 'error')
        except requests.exceptions.RequestException as e:
            flash(f'Error: {e}', 'error')
        return redirect(url_for('products'))

    try:
        response = requests.get(API_URL + '/product/' + str(id))
        if response.status_code == 200:
            product = response.json()
            return render_template('update_product.html', product=product)
        else:
            flash('Product not found', 'error')
            return redirect(url_for('products'))
    except requests.exceptions.RequestException as e:
        flash(f'Error fetching product from API: {e}', 'error')
        return redirect(url_for('products'))

# Route untuk logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('password', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=5501)