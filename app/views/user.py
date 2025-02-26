from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)
from app.utils import *
from app.db.db import get_db, close_db

# Routes /user/...
user_bp = Blueprint('user', __name__, url_prefix='/user')

# Route /user/profile accessible uniquement à un utilisateur connecté grâce au décorateur @login_required
@user_bp.route('/profile', methods=('GET', 'POST'))
@login_required 
def show_profile():
    # Affichage de la page principale de l'application
    return render_template('user/profile.html')

@user_bp.route('/profile/edit', methods=('GET', 'POST'))
@login_required 
def show_profile_edit():
    # Affichage de la page principale de l'application
    return render_template('user/profile_edit.html')

@user_bp.route('/profile/update', methods=['POST'])
@login_required 
def update_profile():
    db = get_db()
    user = db.execute('SELECT * FROM Utilisateurs WHERE id_utilisateurs = ?',
                      (g.user['id_utilisateurs'],)).fetchone()
    if user is None:
        flash("Utilisateur introuvable.", "error")
        return redirect(url_for('user.show_profile'))
    tel = request.form.get('tel') or user['numero_de_telephone']
    mail = request.form.get('mail') or user['mail']
    chesscom = request.form.get('chess_com') or user['chess_com']
    lichess = request.form.get('lichess') or user['lichess']
    
    try:
        db.execute('''
            UPDATE Utilisateurs
            SET numero_de_telephone = ?, mail = ?, chess_com = ?, lichess = ?
            WHERE id_utilisateurs = ?
        ''', (tel, mail, chesscom, lichess, g.user['id_utilisateurs']))
        db.commit()
        flash("Profil mis à jour avec succès !", "success")
    except Exception as e:
        db.rollback()
        flash(f"Une erreur est survenue : {str(e)}", "error")
    finally:
        close_db()

    return redirect(url_for('user.show_profile'))
