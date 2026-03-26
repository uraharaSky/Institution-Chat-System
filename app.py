from flask import Flask
from extensions import db, bcrypt, jwt
from routes.attendance import attendance_bp

def create_app():
    app = Flask(__name__)

    #configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'super-secret-key'

    #initiate extensions
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)

    # Register Blueprints
    from routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    from routes.attendance import attendance_bp

    app.register_blueprint(attendance_bp, url_prefix='/api/attendance')

    return app


app = create_app()

# Create DB tables automatically
with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(debug=True)

