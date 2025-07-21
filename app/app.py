from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token
from models import db, bcrypt, User, WeatherRequest
from config import Config
import requests
from flask import current_app
from flask_cors import CORS
from flask_migrate import Migrate

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://weatherapi-app.azurewebsites.net"}})
app.config.from_object(Config)
# initialize plugins with app
db.init_app(app)
bcrypt.init_app(app)
jwt = JWTManager(app)
migrate = Migrate(app, db)
from flask import send_from_directory

@app.route('/index.html')
def serve_index():
    return send_from_directory('.', 'index.html')

# Home route
@app.route("/")
def home():
    return "🌤️ Weather API is running!"

# Register new user
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    if not data.get("username") or not data.get("password"):
        return jsonify({"message": "Username and password required"}), 400
    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"message": "User already exists"}), 400
    password_hash = bcrypt.generate_password_hash(data["password"]).decode("utf-8")
    new_user = User(username=data["username"], password_hash=password_hash)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered", "api_key": new_user.api_key})

# Login user
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    user = User.query.filter_by(username=data["username"]).first()
    if user and user.check_password(data["password"]):
        token = create_access_token(identity=str(user.id))
        return jsonify({"access_token": token, "api_key": user.api_key})
    return jsonify({"message": "Invalid credentials"}), 401



@app.route("/weather", methods=["GET"])
def get_weather():
    api_key = request.args.get("api_key")
    city = request.args.get("city")

    if not api_key or not city:
        return jsonify({"error": "API key and city are required"}), 400

    # Verify user by API key
    user = User.query.filter_by(api_key=api_key).first()
    if not user:
        return jsonify({"error": "Invalid API key"}), 401

    # Call OpenWeatherMap API
    ow_api_key = current_app.config["OPENWEATHER_API_KEY"]
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={ow_api_key}&units=metric"
    response = requests.get(url)

    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch weather data"}), response.status_code

    data = response.json()

    # Save weather request to DB
    weather_request = WeatherRequest(
        user_id=user.id,
        city=city,
        temperature=data["main"]["temp"],
        description=data["weather"][0]["description"]
    )
    db.session.add(weather_request)
    db.session.commit()

    # Return weather data
    return jsonify({
        "city": city,
        "temperature": data["main"]["temp"],
        "description": data["weather"][0]["description"]
    })

from flask_jwt_extended import jwt_required, get_jwt_identity

@app.route("/me/weather/history", methods=["GET"])
@jwt_required()
def get_my_weather_history():
    user_id = int(get_jwt_identity())

    history = WeatherRequest.query.filter_by(user_id=user_id).order_by(WeatherRequest.timestamp.desc()).all()

    data = [
        {
            "city": entry.city,
            "temperature": entry.temperature,
            "description": entry.description,
            "timestamp": entry.timestamp.isoformat()
        }
        for entry in history
    ]

    return jsonify(data)

from flask_jwt_extended import jwt_required, get_jwt, unset_jwt_cookies

# Token blacklist storage (in-memory for now)
jwt_blacklist = set()

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    return jti in jwt_blacklist

@app.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]  # JWT ID
    jwt_blacklist.add(jti)  # Revoke the token
    response = jsonify({"msg": "Successfully logged out"})
    unset_jwt_cookies(response)  # Optional: clear token in cookies if used
    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)