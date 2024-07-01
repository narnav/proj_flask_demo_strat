from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc
from flask_cors import CORS  # Import CORS from flask_cors module
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity


app = Flask(__name__)
# Initialize CORS with default options
CORS(app)
# Initialize Flask-Bcrypt
bcrypt = Bcrypt(app)
# Initialize Flask-JWT-Extended
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'  # Change this to a secure secret key
jwt = JWTManager(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cars.db'  # SQLite database file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define the Car model
class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    color = db.Column(db.String(50), nullable=False)
    brand = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    owner = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<Car {self.id}: {self.color} {self.brand} {self.model} - Owned by: {self.owner}>'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='user', nullable=False)  # Default role is 'user'

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)


@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'user')  # Default role is 'user'

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    # Check if the username already exists
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 400

    # Create a new user
    new_user = User(username=username, role=role)
    new_user.set_password(password)

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'User registered successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500





# Define a test endpoint
@app.route('/test', methods=['GET'])
def test():
    return "{'test':'success'}"


#TODO add login endpoint

# Define a test endpoint
@app.route('/', methods=['GET'])
def home():
    return 'build login regi' #

# Create a new car
@app.route('/cars', methods=['POST'])
def create_car():
    data = request.json
    new_car = Car(
        color=data['color'],
        brand=data['brand'],
        model=data['model'],
        owner=data['owner']  # Include owner in the creation
    )
    try:
        db.session.add(new_car)
        db.session.commit()
        return jsonify({'message': 'Car created successfully'}), 201
    except exc.IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Car with this ID already exists'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# Retrieve all cars
@app.route('/cars', methods=['GET'])
def get_all_cars():
    cars = Car.query.all()
    car_list = []
    for car in cars:
        car_list.append({
            'id': car.id,
            'color': car.color,
            'brand': car.brand,
            'model': car.model,
            'owner': car.owner  # Include owner in the response
        })
    return jsonify(car_list), 200


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    user = User.query.filter_by(username=username).first()

    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid username or password'}), 401

    # Generate JWT token with username and role
    access_token = create_access_token(identity={'username': username, 'role': user.role})
    return jsonify({'access_token': access_token}), 200

@app.route('/admin', methods=['GET'])
@jwt_required()
def admin():
    current_user = get_jwt_identity()
    username = current_user.get('username')
    role = current_user.get('role')

    if role != 'admin':
        return jsonify({'error': 'Unauthorized access'}), 403

    # Logic for admin-only functionality
    return jsonify({'message': f'Welcome, {username}. You have admin privileges!'}), 200


# Protected route example
@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200


if __name__ == '__main__':
    # Create all database tables
    with app.app_context():
        db.create_all()
    app.run(debug=True)
