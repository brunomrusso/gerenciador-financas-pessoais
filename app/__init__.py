from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import os
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
jwt = JWTManager()

def create_app(config_name='development'):
    app = Flask(__name__)
    
    from config import config
    app.config.from_object(config[config_name])
    
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)
    
    with app.app_context():
        from app.models import User, MonthlyRecord, Discount, Expense, CardDetail, Investment, Category
        db.create_all()
        
        from app.routes import auth_routes, records_routes
        app.register_blueprint(auth_routes.bp)
        app.register_blueprint(records_routes.bp)
    
    return app
