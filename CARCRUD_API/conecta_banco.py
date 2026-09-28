import hashlib
import hmac
import os
import sqlite3

# O banco fica na mesma pasta do projeto (ou no caminho definido em DATABASE_PATH).
DB_PATH = os.getenv(
    "DATABASE_PATH",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "conecta_banco.db"),
)

con = sqlite3.connect(DB_PATH, check_same_thread=False)
con.execute("PRAGMA foreign_keys = ON")


def criar_tabelas():
    cursor = con.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS VEICULO (
            id_veiculo INTEGER PRIMARY KEY NOT NULL,
            placa TEXT UNIQUE NOT NULL,
            marca TEXT NOT NULL,
            ano INTEGER NOT NULL,
            modelo TEXT NOT NULL,
            valor_de_compra REAL NOT NULL,
            status TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS DESPESAS (
            id_veiculo INTEGER NOT NULL,
            titulo TEXT NOT NULL,
            valor_gasto REAL NOT NULL,
            descricao TEXT NOT NULL,
            FOREIGN KEY (id_veiculo) REFERENCES VEICULO (id_veiculo)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS VENDA (
            id_veiculo INTEGER NOT NULL,
            valor_vendido REAL NOT NULL,
            nome_comprador TEXT NOT NULL,
            FOREIGN KEY (id_veiculo) REFERENCES VEICULO (id_veiculo)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuario (
            usuario TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL
        )
    ''')

    con.commit()


# ---------- Senhas ----------

def gerar_hash_senha(senha):
    """Gera 'salt$hash' com PBKDF2. A senha nunca é guardada em texto puro."""
    salt = os.urandom(16)
    hash_ = hashlib.pbkdf2_hmac("sha256", senha.encode(), salt, 200_000)
    return f"{salt.hex()}${hash_.hex()}"


def verificar_senha(senha, senha_hash):
    try:
        salt_hex, hash_hex = senha_hash.split("$")
        salt = bytes.fromhex(salt_hex)
    except ValueError:
        return False
    novo_hash = hashlib.pbkdf2_hmac("sha256", senha.encode(), salt, 200_000)
    return hmac.compare_digest(novo_hash.hex(), hash_hex)


# ---------- Usuários ----------

def inserir_usuario(user, senha, con=con):
    """Levanta sqlite3.IntegrityError se o usuário já existir."""
    cursor = con.cursor()
    cursor.execute(
        "INSERT INTO usuario (usuario, senha) VALUES (?, ?)",
        (user, gerar_hash_senha(senha)),
    )
    con.commit()


def consultar_usuario(user, senha, con=con):
    """Retorna o nome do usuário se as credenciais forem válidas, senão None."""
    cursor = con.cursor()
    linha = cursor.execute(
        "SELECT usuario, senha FROM usuario WHERE usuario = ?", (user,)
    ).fetchone()
    if linha and verificar_senha(senha, linha[1]):
        return linha[0]
    return None


# ---------- Veículos ----------

def salvar_carro(placa, marca, ano, modelo, status, valor_compra, con=con):
    """Retorna True se salvou, False se a placa já existe ou falta algum campo."""
    cursor = con.cursor()
    try:
        cursor.execute(
            '''INSERT INTO VEICULO
                   (placa, marca, ano, modelo, status, valor_de_compra)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (placa, marca, ano, modelo, status, valor_compra),
        )
    except sqlite3.IntegrityError:
        return False
    con.commit()
    return True


def carro_existe(id_veiculo, con=con):
    cursor = con.cursor()
    linha = cursor.execute(
        "SELECT 1 FROM VEICULO WHERE id_veiculo = ?", (id_veiculo,)
    ).fetchone()
    return linha is not None


def consultar_carros(con=con):
    cursor = con.cursor()
    return cursor.execute("SELECT * FROM VEICULO").fetchall()


def consultar_carro_especifico(placa, con=con):
    cursor = con.cursor()
    return cursor.execute(
        "SELECT * FROM VEICULO WHERE placa = ?", (placa,)
    ).fetchall()


# ---------- Despesas ----------

def salvar_despesa(id_veiculo, titulo, valor_gasto, descricao, con=con):
    cursor = con.cursor()
    cursor.execute(
        '''INSERT INTO DESPESAS (id_veiculo, titulo, valor_gasto, descricao)
           VALUES (?, ?, ?, ?)''',
        (id_veiculo, titulo, valor_gasto, descricao),
    )
    con.commit()


def consultar_gasto_veiculo(id_veiculo, con=con):
    cursor = con.cursor()
    return cursor.execute(
        '''SELECT id_veiculo, titulo, descricao, valor_gasto
           FROM DESPESAS WHERE id_veiculo = ?''',
        (id_veiculo,),
    ).fetchall()


def gerar_total_gasto_veiculo(id_veiculo, con=con):
    """Resumo do veículo: dados, valor de compra e total gasto em despesas."""
    cursor = con.cursor()
    return cursor.execute(
        '''SELECT v.id_veiculo,
                  v.placa,
                  v.marca || ' - ' || v.modelo || ' - ' || v.ano,
                  v.valor_de_compra,
                  COALESCE(SUM(d.valor_gasto), 0)
           FROM VEICULO v
           LEFT JOIN DESPESAS d ON d.id_veiculo = v.id_veiculo
           WHERE v.id_veiculo = ?
           GROUP BY v.id_veiculo''',
        (id_veiculo,),
    ).fetchall()


# ---------- Vendas ----------

def vender_carro(id_veiculo, valor_vendido, nome_comprador, con=con):
    cursor = con.cursor()
    cursor.execute(
        '''INSERT INTO VENDA (id_veiculo, valor_vendido, nome_comprador)
           VALUES (?, ?, ?)''',
        (id_veiculo, valor_vendido, nome_comprador),
    )
    cursor.execute(
        "UPDATE VEICULO SET status = 'vendido' WHERE id_veiculo = ?",
        (id_veiculo,),
    )
    con.commit()
