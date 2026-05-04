"""
Script para criar as tabelas no banco de dados PostgreSQL.
Execute: python init_db.py
"""
import sys
import os
from dotenv import load_dotenv

load_dotenv()

try:
    from app import create_app, db
    app = create_app()

    with app.app_context():
        db.create_all()
        print("[OK] Tabelas criadas com sucesso!")
        print("\nTabelas criadas:")
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        for table in inspector.get_table_names():
            print(f"  - {table}")

except Exception as e:
    print(f"[ERRO] {e}")
    sys.exit(1)
