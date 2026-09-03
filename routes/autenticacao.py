
from flask import Blueprint, render_template, session, redirect, url_for, request
from banco.conexao import cursor

autenticacao_bp = Blueprint("auth", __name__)


# ROTA PRINCIPAL - METODO GET -----------------------
# Se o usuário já estiver logado no sistema web, então ele será redirecionado para a página de painel, se não, ele irá para a página de login.

@autenticacao_bp.route("/", methods=["GET"])
def index(): 
    
    if "matricula" in session:
        return redirect(url_for("painel"))
    return redirect(url_for("login"))


# ROTA DE LOGIN - METODOS GET E POST --------------------------------------------------
# Página para o usuário fazer login. O sistema checa no DB se o usuário está cadastrado.

@autenticacao_bp.route("/login", methods=["GET", "POST"])
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

@autenticacao_bp.route("/painel")
def painel():
    # Protege a rota: só entra quem já fez login
    if "matricula" not in session:
        return redirect(url_for("login"))

    return render_template(
        "painel.html",
        nome=session["nome"],
        perfil=session["perfil"],
    )
    

# ROTA DE LOGOUT - METODO GET: ---------------

@autenticacao_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))