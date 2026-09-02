from flask import Flask, render_template, request, session, redirect, url_for
from dotenv import load_dotenv
import os

load_dotenv()

from banco.conexao import db, cursor

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")


# ROTA PRINCIPAL - METODO GET -----------------------
# Se o usuário já estiver logado no sistema web, então ele será redirecionado para a página de painel, se não, ele irá para a página de login.
@app.route("/", methods=["GET"])
def index(): 
    
    if "matricula" in session:
        return redirect(url_for("painel"))
    return redirect(url_for("login"))


# ROTA DE LOGIN - METODOS GET E POST --------------------------------------------------
# Página para o usuário fazer login. O sistema checa no DB se o usuário está cadastrado.
@app.route("/login", methods=["GET", "POST"])
def login():
    erro = None

    if request.method == "POST":
        matricula = request.form.get("matricula", "").strip()

        if not (len(matricula) == 4 and matricula.isdigit()):
            erro = "Digite exatamente 4 números."
        else:
            cursor.execute(
                """
                SELECT nome, matricula, perfil
                FROM usuarios
                WHERE matricula = %s
                """,
                (matricula,),
            )
            usuario = cursor.fetchone()

            if usuario:
                nome, matricula, perfil = usuario
                
                session["nome"] = nome
                session["matricula"] = matricula
                session["perfil"] = perfil
                return redirect(url_for("painel"))
            else:
                erro = "Usuário não encontrado."

    return render_template("login.html", erro=erro)

# ROTA PAINEL - METODO GET -------------------------------------------------------
# Mostra o painel principal do sistema, onde pode ser acessado os menus do HTML
@app.route("/painel")
def painel():
    # Protege a rota: só entra quem já fez login
    if "matricula" not in session:
        return redirect(url_for("login"))

    return render_template(
        "painel.html",
        nome=session["nome"],
        perfil=session["perfil"],
    )


# ROTA DE CHAMADOS - METODO GET: ---------------------------------------
# Lista TODOS os chamados armazenados no DB (Apenas os TIs podem ver)
@app.route("/chamados")
def listar_chamados():

    if "matricula" not in session:
        return redirect(url_for("login"))

    if session["perfil"] != "TI":
        return redirect(url_for("painel"))
    
    cursor.execute(
        """
        SELECT id, titulo, categoria, prioridade, status
        FROM chamados
        ORDER BY id DESC
        """
    )
    chamados = cursor.fetchall()

    return render_template("chamados.html", chamados=chamados)


# ROTA DE CHAMADOS POR USUÁRIO - METODO GET: ---------------------------
# Rota para ver informações de todos os chamados que um usuário abriu
@app.route("/meus-chamados")
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


# ROTA PARA CADASTRAR USUÁRIOS - METODOS GET E POST: -----------------------
# Rota que apenas os TIs acessam e cadastram um novo usuairo no DB.
@app.route("/cadastrar-usuario", methods=["GET", "POST"])
def cadastrar_usuario():

    if "matricula" not in session:
        return redirect(url_for("login"))

    if session["perfil"] != "TI":
        return redirect(url_for("painel"))

    erro = None

    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        perfil = request.form.get("perfil", "").strip()
        email = request.form.get("email", "").strip().lower()
        matricula = request.form.get("matricula", "").strip()

        if not nome:
            erro = "O nome não pode ficar vazio."
        elif not perfil:
            erro = "O perfil do usuário não pode ficar vazio"
        elif not perfil in ["TI", "Usuario"]:
            erro = "O perfil do usuário deve ser 'TI' ou 'Usuario'"
        elif not email:
            erro = "O e-mail não pode ficar vazio."
        elif not (len(matricula) == 4 and matricula.isdigit()):
            erro = "A matrícula precisa ter exatamente 4 números."
        else:
            cursor.execute(
                "SELECT id FROM usuarios WHERE email = %s",
                (email,),
            )
            if cursor.fetchone():
                erro = "Já existe um usuário com esse e-mail."


        if erro is None:
            cursor.execute(
                "SELECT id FROM usuarios WHERE matricula = %s",
                (matricula,),
            )
            if cursor.fetchone():
                erro = "Já existe um usuário com essa matrícula."

        if erro is None:
            cursor.execute(
                """
                INSERT INTO usuarios (nome, perfil, email, matricula)
                VALUES (%s, %s, %s, %s)
                """,
                (nome, perfil, email, matricula),
            )
            db.commit()

            return redirect(url_for("painel"))

    return render_template("cadastrar_usuario.html", erro=erro)


# ROTA PARA MUDAR O STATUS DE UM CHAMADO - METODO POST: --------------------
# Nessa rota apenas os TIs conseguem acessar e mudar o status de um chamado especifico.
@app.route("/chamados/<int:id_chamado>/status", methods=["POST"])
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
@app.route("/abrir-chamado", methods=["GET", "POST"])
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

# ROTA DO DASHBOARD - METODO GET: ----------------------------------
# Rota que mostra um dashboard com informações de todos os chamados. Apenas os TIs podem ver
@app.route("/dashboard")
def dashboard():
    
    if "matricula" not in session:
        return redirect(url_for("login"))

    if session["perfil"] != "TI":
        return redirect(url_for("painel"))

    cursor.execute("SELECT COUNT(id) FROM usuarios;")
    tot_usuarios = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(id) FROM chamados;")
    tot_chamados = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COUNT(id)
        FROM chamados
        WHERE status IN ('Aberto', 'Em andamento');
        """
    )
    chamados_abertos = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COUNT(id)
        FROM chamados
        WHERE status = 'Fechado';
        """
    )
    chamados_fechados = cursor.fetchone()[0]

    return render_template(
        "dashboard.html",
        tot_usuarios=tot_usuarios,
        tot_chamados=tot_chamados,
        chamados_abertos=chamados_abertos,
        chamados_fechados=chamados_fechados,
    )


# ROTA DE LOGOUT - METODO GET: ---------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)