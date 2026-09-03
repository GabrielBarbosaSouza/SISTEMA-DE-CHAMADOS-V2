from flask import Blueprint, render_template, session, redirect, url_for
from banco.conexao import cursor

dashboard_bp = Blueprint("dashboard", __name__)


# ROTA DO DASHBOARD - METODO GET: ----------------------------------
# Rota que mostra um dashboard com informações de todos os chamados. Apenas os TIs podem ver

@dashboard_bp.route("/dashboard")
def dashboard():

    if "matricula" not in session:
        return redirect(url_for("auth.login"))

    if session["perfil"] != "TI":
        return redirect(url_for("auth.painel"))

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