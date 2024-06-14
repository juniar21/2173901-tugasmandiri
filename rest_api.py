from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)

# Model untuk User
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# Schema untuk User
class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True

user_schema = UserSchema()
users_schema = UserSchema(many=True)

# Model untuk Product
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    price = db.Column(db.Float, nullable=False)

# Schema untuk Product
class ProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Product
        load_instance = True

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)


# Endpoint untuk register user
@app.route('/register', methods=['POST'])
def register():
    username = request.json['username']
    password = generate_password_hash(request.json['password'])
    
    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()
    
    return user_schema.jsonify(new_user)

# Endpoint untuk login user
@app.route('/login', methods=['POST'])
def login():
    username = request.json['username']
    password = request.json['password']
    
    user = User.query.filter_by(username=username).first()
    
    if user and check_password_hash(user.password, password):
        return user_schema.jsonify(user)
    else:
        return jsonify({"message": "Invalid credentials"}), 401

# Endpoint untuk menambahkan product
@app.route('/product', methods=['POST'])
def add_product():
    name = request.json['name']
    description = request.json.get('description', '')
    price = request.json['price']
    
    new_product = Product(name=name, description=description, price=price)
    db.session.add(new_product)
    db.session.commit()
    
    return product_schema.jsonify(new_product)

# Endpoint untuk mendapatkan semua produk
@app.route('/products', methods=['GET'])
def get_products():
    all_products = Product.query.all()
    return products_schema.jsonify(all_products)

# Endpoint untuk mengupdate product
@app.route('/product/<int:id>', methods=['PUT'])
def update_product(id):
    product = Product.query.get(id)
    
    if product:
        product.name = request.json['name']
        product.description = request.json.get('description', product.description)
        product.price = request.json['price']
        
        db.session.commit()
        return product_schema.jsonify(product)
    else:
        return jsonify({"message": "Product not found"}), 404

# Endpoint untuk menghapus product
@app.route('/product/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get(id)
    
    if product:
        db.session.delete(product)
        db.session.commit()
        return product_schema.jsonify(product)
    else:
        return jsonify({"message": "Product not found"}), 404

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5500)