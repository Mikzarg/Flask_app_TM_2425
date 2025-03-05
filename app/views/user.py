from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)
from app.utils import *
from app.db.db import get_db, close_db

# Routes /user/...
user_bp = Blueprint('user', __name__, url_prefix='/user')

# Route /user/profile accessible uniquement à un utilisateur connecté grâce au décorateur @login_required
@user_bp.route('/', methods=('GET', 'POST'))
@login_required 
def show_profile():
    # Affichage de la page principale de l'application
    return render_template('user/profile.html')

@user_bp.route('/edit', methods=('GET', 'POST'))
@login_required 
def show_profile_edit():
    # Affichage de la page principale de l'application
    return render_template('user/profile_edit.html')

@user_bp.route('/update', methods=['POST'])
@login_required 
def update_profile():
    db = get_db()
    tel = request.form.get('tel')
    mail = request.form.get('mail')
    chesscom = request.form.get('chess_com')
    lichess = request.form.get('lichess')
    sexe = request.form.get('sexe')
    
    try:
        db.execute('''
            UPDATE Utilisateurs
            SET numero_de_telephone = ?, mail = ?, chess_com = ?, lichess = ?, sexe= ?
            WHERE id_utilisateurs = ?
        ''', (tel, mail, chesscom, lichess, sexe, g.user['id_utilisateurs']))
        db.commit()
        flash("Profil mis à jour avec succès !", "success")
    except Exception as e:
        db.rollback()
        flash(f"Une erreur est survenue : {str(e)}", "error")
    finally:
        close_db()

    return redirect(url_for('user.show_profile'))
