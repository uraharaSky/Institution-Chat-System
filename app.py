import app
from flask import Flask
from extensions import db, bcrypt, jwt
from routes.attendance import attendance_bp
from routes.chats import chat_bp
from routes.notices import notice_bp
from routes.polls import poll_bp
from routes.admin import admin_bp
from routes.auth import auth_bp
from routes.groups import groups_bp
from routes.notification import notif_bp

import requests

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
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    app.register_blueprint(attendance_bp, url_prefix='/api/attendance')

    app.register_blueprint(notice_bp, url_prefix='/api/notices')

    app.register_blueprint(poll_bp, url_prefix='/api/polls')

    app.register_blueprint(admin_bp, url_prefix='/api/admin')

    app.register_blueprint(chat_bp, url_prefix="/chat")


    app.register_blueprint(groups_bp)

    app.register_blueprint(notif_bp)


    return app


app = create_app()

# Create DB tables automatically
with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
