import os
from dotenv import load_dotenv
from app import create_app, db

load_dotenv()

app = create_app(os.getenv('FLASK_ENV', 'development'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    port = int(os.getenv('PORT', 5000))
    host = '0.0.0.0' if os.getenv('FLASK_ENV') == 'production' else '127.0.0.1'
    app.run(debug=os.getenv('FLASK_DEBUG', 'true').lower() == 'true', host=host, port=port)
