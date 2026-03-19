from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
from database import (
    criar_tabelas,
    listar_exames,
    buscar_exame_por_nome,
    inserir_agendamento,
    listar_agendamentos
)

app = Flask(__name__)

# Inicializa tabelas
criar_tabelas()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/exames", methods=["GET"])
def api_listar_exames():
    try:
        exames = listar_exames()
        return jsonify(exames), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route("/api/exames/buscar", methods=["GET"])
def api_buscar_exames():
    try:
        termo = request.args.get("termo", "").strip()

        if not termo:
            return jsonify([]), 200

        resultados = buscar_exame_por_nome(termo)
        return jsonify(resultados), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route("/api/agendamentos", methods=["GET"])
def api_listar_agendamentos():
    try:
        dados = listar_agendamentos()

        agendamentos_formatados = []
        for item in dados:
            novo_item = dict(item)

            if "data_agendamento" in novo_item and novo_item["data_agendamento"]:
                if hasattr(novo_item["data_agendamento"], "strftime"):
                    novo_item["data_agendamento"] = novo_item["data_agendamento"].strftime("%Y-%m-%d")
                else:
                    novo_item["data_agendamento"] = str(novo_item["data_agendamento"])

            if "horario" in novo_item and novo_item["horario"]:
                horario = novo_item["horario"]

                if hasattr(horario, "strftime"):
                    novo_item["horario"] = horario.strftime("%H:%M")
                elif isinstance(horario, timedelta):
                    total_segundos = int(horario.total_seconds())
                    horas = total_segundos // 3600
                    minutos = (total_segundos % 3600) // 60
                    novo_item["horario"] = f"{horas:02d}:{minutos:02d}"
                else:
                    novo_item["horario"] = str(horario)

            agendamentos_formatados.append(novo_item)

        return jsonify(agendamentos_formatados), 200

    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route("/api/agendamentos", methods=["POST"])
def api_criar_agendamento():
    try:
        data = request.get_json()

        nome_paciente = data.get("nome_paciente", "").strip()
        telefone = data.get("telefone", "").strip()
        exame = data.get("exame", "").strip()
        data_agendamento = data.get("data_agendamento", "").strip()
        horario = data.get("horario", "").strip()
        observacoes = data.get("observacoes", "").strip()

        if not nome_paciente:
            return jsonify({"erro": "Informe o nome do paciente."}), 400

        if not telefone:
            return jsonify({"erro": "Informe o telefone."}), 400

        if not exame:
            return jsonify({"erro": "Informe o exame."}), 400

        if not data_agendamento:
            return jsonify({"erro": "Informe a data do agendamento."}), 400

        if not horario:
            return jsonify({"erro": "Informe o horário."}), 400

        data_convertida = datetime.strptime(data_agendamento, "%Y-%m-%d").date()
        horario_convertido = datetime.strptime(horario, "%H:%M").time()

        inserir_agendamento(
            nome_paciente=nome_paciente,
            telefone=telefone,
            exame=exame,
            data_agendamento=data_convertida,
            horario=horario_convertido,
            observacoes=observacoes
        )

        return jsonify({"mensagem": "Agendamento salvo com sucesso!"}), 201

    except ValueError:
        return jsonify({"erro": "Data ou horário em formato inválido."}), 400
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)