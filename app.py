from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc
from flask_cors import CORS  # Import CORS from flask_cors module

app = Flask(__name__)
# Initialize CORS with default options
CORS(app)

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


if __name__ == '__main__':
    # Create all database tables
    with app.app_context():
        db.create_all()
    app.run(debug=True)
