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
    CORS(app, resources={r'/api/*': {'origins': '*'}}, supports_credentials=True)
    
    with app.app_context():
        from app.models import (
            User, MonthlyRecord, Discount, Expense, CardDetail, Investment, Category,
            CardPayment, TelegramLink, TelegramLinkCode
        )
        db.create_all()
        
        try:
            from sqlalchemy import text
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE expenses ADD COLUMN IF NOT EXISTS recorrente BOOLEAN DEFAULT FALSE"))
                conn.execute(text("ALTER TABLE card_expenses ADD COLUMN IF NOT EXISTS categoria VARCHAR(100) DEFAULT 'Outros'"))
                conn.execute(text("ALTER TABLE card_expenses ADD COLUMN IF NOT EXISTS group_id VARCHAR(36)"))
                conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS nome VARCHAR(100)"))
                conn.execute(text("ALTER TABLE categories ADD COLUMN IF NOT EXISTS orcamento FLOAT DEFAULT 0"))
                conn.execute(text("ALTER TABLE expenses ADD COLUMN IF NOT EXISTS tags VARCHAR(255)"))
                conn.execute(text("ALTER TABLE card_expenses ADD COLUMN IF NOT EXISTS tags VARCHAR(255)"))
                conn.execute(text("ALTER TABLE expenses ADD COLUMN IF NOT EXISTS account_id INTEGER REFERENCES financial_accounts(id)"))
                conn.execute(text("ALTER TABLE discounts ADD COLUMN IF NOT EXISTS account_id INTEGER REFERENCES financial_accounts(id)"))
                conn.execute(text("ALTER TABLE discounts ADD COLUMN IF NOT EXISTS recorrente BOOLEAN DEFAULT FALSE"))
                conn.execute(text("ALTER TABLE investment_transactions ADD COLUMN IF NOT EXISTS financial_account_id INTEGER REFERENCES financial_accounts(id)"))
                conn.commit()
        except Exception:
            pass
        
        from app.routes import auth_routes, records_routes, cards_routes, investments_routes, accounts_routes, telegram_routes
        app.register_blueprint(auth_routes.bp)
        app.register_blueprint(records_routes.bp)
        app.register_blueprint(cards_routes.bp)
        app.register_blueprint(investments_routes.bp)
        app.register_blueprint(accounts_routes.bp)
        app.register_blueprint(telegram_routes.bp)

    # Healthcheck publico (sem auth) - usado por keepalive externo (Render free nao dormir)
    @app.route('/health')
    def health():
        return {'status': 'ok'}, 200

    # Bot Telegram (thread separada, opcional)
    if os.getenv('TELEGRAM_BOT_ENABLED', '').lower() == 'true' and os.getenv('TELEGRAM_BOT_TOKEN'):
        try:
            from app.telegram_bot import start_bot_thread
            start_bot_thread(app)
            print('[Telegram] Bot iniciado em thread separada')
        except Exception as e:
            print(f'[Telegram] Falha ao iniciar bot: {e}')

    return app
