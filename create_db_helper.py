"""
Script auxiliar para criar o banco de dados PostgreSQL.
Usado pelo create_db.ps1 - nao requer psql no PATH.
"""
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_database(host, port, user, password, dbname="financas_db"):
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            dbname="postgres"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()

        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (dbname,))
        exists = cur.fetchone()

        if exists:
            print(f"[AVISO] Banco de dados '{dbname}' ja existe.")
        else:
            cur.execute(f'CREATE DATABASE "{dbname}"')
            print(f"[OK] Banco de dados '{dbname}' criado com sucesso!")

        cur.close()
        conn.close()
        return True

    except psycopg2.OperationalError as e:
        print(f"[ERRO] Nao foi possivel conectar ao PostgreSQL: {e}")
        return False
    except Exception as e:
        print(f"[ERRO] {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Uso: python create_db_helper.py <host> <port> <user> <password>")
        sys.exit(1)

    host = sys.argv[1]
    port = sys.argv[2]
    user = sys.argv[3]
    password = sys.argv[4] if len(sys.argv) > 4 else ""

    success = create_database(host, port, user, password)
    sys.exit(0 if success else 1)
