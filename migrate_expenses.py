"""
Migração: adicionar campos categoria, data e pago na tabela expenses.
Execute: python migrate_expenses.py
"""
import psycopg2
from dotenv import load_dotenv
import os, re

load_dotenv()

db_url = os.getenv('DATABASE_URL', '')
match = re.match(r'postgresql://([^@]*)@([^/]+)/(.+)', db_url)
if not match:
    print("[ERRO] DATABASE_URL inválida:", db_url)
    exit(1)

user_pass, host_port, dbname = match.group(1), match.group(2), match.group(3)
user = user_pass.split(':')[0]
password = user_pass.split(':')[1] if ':' in user_pass else ''
host = host_port.split(':')[0]
port = host_port.split(':')[1] if ':' in host_port else '5432'

conn = psycopg2.connect(host=host, port=port, user=user, password=password, dbname=dbname)
conn.autocommit = True
cur = conn.cursor()

migrations = [
    ("categoria", "ALTER TABLE expenses ADD COLUMN IF NOT EXISTS categoria VARCHAR(100) DEFAULT 'Outros'"),
    ("data",      "ALTER TABLE expenses ADD COLUMN IF NOT EXISTS data VARCHAR(10)"),
    ("pago",      "ALTER TABLE expenses ADD COLUMN IF NOT EXISTS pago BOOLEAN DEFAULT FALSE"),
]

for name, sql in migrations:
    try:
        cur.execute(sql)
        print(f"[OK] Coluna '{name}' adicionada")
    except Exception as e:
        print(f"[AVISO] '{name}': {e}")

cur.close()
conn.close()
print("\n[CONCLUIDO] Migração finalizada!")
