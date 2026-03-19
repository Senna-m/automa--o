import mysql.connector

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "port": int(os.getenv("DB_PORT", 3306))
}

def conectar():
    return mysql.connector.connect(**DB_CONFIG)


def criar_tabelas():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS exames (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome_exame VARCHAR(150) NOT NULL,
            preparo TEXT,
            amostra VARCHAR(100),
            prazo VARCHAR(50),
            orientacao TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agendamentos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome_paciente VARCHAR(150) NOT NULL,
            telefone VARCHAR(30) NOT NULL,
            exame VARCHAR(150) NOT NULL,
            data_agendamento DATE NOT NULL,
            horario TIME NOT NULL,
            observacoes TEXT
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()


def listar_exames():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT nome_exame FROM exames ORDER BY nome_exame")
    resultados = cursor.fetchall()

    cursor.close()
    conn.close()

    return [item[0] for item in resultados]


def buscar_exame_por_nome(nome_exame):
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    sql = """
        SELECT nome_exame, preparo, amostra, prazo, orientacao
        FROM exames
        WHERE nome_exame LIKE %s
        ORDER BY nome_exame
    """
    cursor.execute(sql, (f"%{nome_exame}%",))
    resultados = cursor.fetchall()

    cursor.close()
    conn.close()

    return resultados


def inserir_agendamento(nome_paciente, telefone, exame, data_agendamento, horario, observacoes):
    conn = conectar()
    cursor = conn.cursor()

    sql = """
        INSERT INTO agendamentos
        (nome_paciente, telefone, exame, data_agendamento, horario, observacoes)
        VALUES (%s, %s, %s, %s, %s, %s)
    """

    valores = (
        nome_paciente,
        telefone,
        exame,
        data_agendamento,
        horario,
        observacoes
    )

    cursor.execute(sql, valores)
    conn.commit()

    cursor.close()
    conn.close()


def listar_agendamentos():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            id,
            nome_paciente,
            telefone,
            exame,
            data_agendamento,
            horario,
            observacoes
        FROM agendamentos
        ORDER BY data_agendamento, horario
    """)

    resultados = cursor.fetchall()

    cursor.close()
    conn.close()

    return resultados