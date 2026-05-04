"""
Script para testar conexao com PostgreSQL e listar usuarios.
Execute: python test_connection.py
"""
import sys
import getpass

try:
    import psycopg2
except ImportError:
    print("[ERRO] psycopg2 nao instalado. Ative o venv primeiro:")
    print("  .\\venv\\Scripts\\Activate.ps1")
    sys.exit(1)

def test_connection(host, port, user, password):
    try:
        conn = psycopg2.connect(
            host=host, port=port, user=user, password=password, dbname="postgres"
        )
        print(f"[OK] Conexao bem-sucedida como '{user}'!")

        cur = conn.cursor()
        cur.execute("SELECT usename FROM pg_user ORDER BY usename;")
        users = [row[0] for row in cur.fetchall()]
        print(f"\nUsuarios existentes no PostgreSQL:")
        for u in users:
            print(f"  - {u}")

        cur.execute("SELECT datname FROM pg_database WHERE datistemplate = false ORDER BY datname;")
        dbs = [row[0] for row in cur.fetchall()]
        print(f"\nBancos de dados existentes:")
        for d in dbs:
            print(f"  - {d}")

        cur.close()
        conn.close()
        return True
    except psycopg2.OperationalError as e:
        print(f"[ERRO] {e}")
        return False

if __name__ == "__main__":
    print("=== Teste de Conexao PostgreSQL ===\n")
    host = input("Host (padrao: localhost): ").strip() or "localhost"
    port = input("Porta (padrao: 5432): ").strip() or "5432"
    user = input("Usuario PostgreSQL: ").strip()
    password = getpass.getpass("Senha: ")

    test_connection(host, port, user, password)
