from flask import Blueprint, render_template, session, redirect, url_for, request
from banco.conexao import cursor, db

chamados_bp = Blueprint("dashboard", __name__)


# ROTA DE CHAMADOS - METODO GET: ---------------------------------------
# Lista TODOS os chamados armazenados no DB (Apenas os TIs podem ver)

@chamados_bp.route("/chamados")
def listar_chamados():

    if "matricula" not in session:
        return redirect(url_for("login"))

    if session["perfil"] != "TI":
        return redirect(url_for("painel"))
    
    cursor.execute(
        """
        SELECT id, titulo, descricao, categoria, prioridade, status, data_abertura, data_fechamento
        FROM chamados
        ORDER BY id DESC
        """
    )
    chamados = cursor.fetchall()

    return render_template("chamados.html", chamados=chamados)


# ROTA DE CHAMADOS POR USUÁRIO - METODO GET: ---------------------------
# Rota para ver informações de todos os chamados que um usuário abriu

@chamados_bp.route("/meus-chamados")
def meus_chamados():

    if "matricula" not in session:
        return redirect(url_for("login"))

    cursor.execute(
        """
        SELECT c.id, c.titulo, c.categoria, c.prioridade, status
        FROM chamados AS c
        JOIN usuarios AS u
            ON c.id_usuario = u.id
        WHERE u.matricula = %s
        ORDER BY id DESC
        """,
        (session["matricula"],),
    )
    chamados = cursor.fetchall()

    return render_template("meus_chamados.html", chamados=chamados)


# ROTA PARA MUDAR O STATUS DE UM CHAMADO - METODO POST: --------------------
# Nessa rota apenas os TIs conseguem acessar e mudar o status de um chamado especifico.

@chamados_bp.route("/chamados/<int:id_chamado>/status", methods=["POST"])
def mudar_status(id_chamado):

    if "matricula" not in session:
        return redirect(url_for("login"))

    if session["perfil"] != "TI":
        return redirect(url_for("painel"))

    acao = request.form.get("acao")

    cursor.execute(
        "SELECT status FROM chamados WHERE id = %s",
        (id_chamado,),
    )
    resultado = cursor.fetchone()

    if resultado is None:
        return redirect(url_for("listar_chamados"))

    status_atual = resultado[0]

    if acao == "atender" and status_atual == "Aberto":
        cursor.execute(
            "UPDATE chamados SET status = 'Em andamento' WHERE id = %s",
            (id_chamado,),
        )
        db.commit()

    elif acao == "fechar" and status_atual != "Fechado":
        cursor.execute(
            "UPDATE chamados SET status = 'Fechado', data_fechamento = NOW() WHERE id = %s",
            (id_chamado,),
        )
        db.commit()

    elif acao == "reabrir" and status_atual == "Fechado":
        cursor.execute(
            "UPDATE chamados SET status = 'Aberto', data_fechamento = NULL WHERE id = %s",
            (id_chamado,),
        )
        db.commit()

    return redirect(url_for("listar_chamados"))

# ROTA DE ABRIR CHAMADO - METODOS GET E POST: ----------------------
# Rota onde os usuários abrem seus chamados.

@chamados_bp.route("/abrir-chamado", methods=["GET", "POST"])
def abrir_chamado():
    
    if "matricula" not in session:
        return redirect(url_for("login"))

    erro = None

    if request.method == "POST":
        titulo = request.form.get("titulo", "").strip()
        descricao = request.form.get("descricao", "").strip()
        categoria = request.form.get("categoria", "").strip()
        prioridade = request.form.get("prioridade", "").strip()

        categorias_validas = ["Hardware", "Software", "Rede", "Impressora"]
        prioridades_validas = ["Baixa", "Media", "Alta"]

        if not titulo:
            erro = "O título não pode ficar vazio."
        elif not descricao:
            erro = "A descrição não pode ficar vazia."
        elif categoria not in categorias_validas:
            erro = "Categoria inválida."
        elif prioridade not in prioridades_validas:
            erro = "Prioridade inválida."
        else:
            cursor.execute(
                "SELECT id FROM usuarios WHERE matricula = %s",
                (session["matricula"],),
            )
            id_usuario = cursor.fetchone()[0]

            cursor.execute(
                """
                INSERT INTO chamados
                (titulo, descricao, categoria, prioridade, id_usuario)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (titulo, descricao, categoria, prioridade, id_usuario),
            )
            db.commit()

            return redirect(url_for("meus_chamados"))

    return render_template("abrir_chamado.html", erro=erro)