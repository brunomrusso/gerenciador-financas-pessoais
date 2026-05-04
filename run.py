import os
from dotenv import load_dotenv
from app import create_app, db

load_dotenv()

app = create_app(os.getenv('FLASK_ENV', 'development'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    app.run(debug=os.getenv('FLASK_DEBUG', True), host='127.0.0.1', port=5000)
