from flask import Blueprint, render_template, session, redirect, url_for, request
from banco.conexao import cursor, db

usuarios_bp = Blueprint("auth", __name__)


# ROTA PARA CADASTRAR USUÁRIOS - METODOS GET E POST: -----------------------
# Rota que apenas os TIs acessam e cadastram um novo usuairo no DB.

@usuarios_bp.route("/cadastrar-usuario", methods=["GET", "POST"])
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