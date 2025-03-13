import os
from werkzeug.utils import secure_filename
from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app)
from app.utils import *
from app.db.db import get_db, close_db

# Routes /user/...
user_bp = Blueprint('user', __name__, url_prefix='/user')
# Définir l'emplacement où sauvegarder les images
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Vérifier si l'extension du fichier est autorisée
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route /user/profile accessible uniquement à un utilisateur connecté grâce au décorateur @login_required
@user_bp.route('/', methods=('GET', 'POST'))
@login_required 
def show_profile():
    db = get_db()
    tournament = db.execute("SELECT * FROM Tournois ORDER BY id_tournoi DESC LIMIT 1").fetchone()
    if tournament:
        g.tournament = tournament
    else:
        g.tournament = None
    user_id = session.get('user_id')
    tournament_id = g.tournament['id_tournoi'] if g.tournament else None
    # Récupérer les tournois joués par l'utilisateur
    user_tournaments = db.execute('''
    SELECT strftime('%Y', T.date_tournoi) AS annee, 
           P.place_au_classement AS place
    FROM Participe P
    JOIN Tournois T ON P.FK_tournoi = T.id_tournoi
    WHERE P.FK_utilisateur = ?
    ORDER BY T.date_tournoi DESC
''', (user_id,)).fetchall()


    # Vérifier si l'utilisateur est inscrit
    is_registered = False
    if user_id and tournament_id:
        existing_entry = db.execute(
            "SELECT 1 FROM Participe WHERE FK_utilisateur = ? AND FK_tournoi = ?",
            (user_id, tournament_id)
        ).fetchone()
        is_registered = bool(existing_entry)
    # Affichage de la page principale de l'application
    return render_template('user/profile.html', is_registered=is_registered, user_tournaments=user_tournaments)

@user_bp.route('/edit', methods=('GET', 'POST'))
@login_required 
def show_profile_edit():
    db = get_db()
    tournament = db.execute("SELECT * FROM Tournois ORDER BY id_tournoi DESC LIMIT 1").fetchone()
    if tournament:
        g.tournament = tournament
    else:
        g.tournament = None
    user_id = session.get('user_id')
    tournament_id = g.tournament['id_tournoi'] if g.tournament else None
    # Vérifier si l'utilisateur est inscrit
    is_registered = False
    if user_id and tournament_id:
        existing_entry = db.execute(
            "SELECT 1 FROM Participe WHERE FK_utilisateur = ? AND FK_tournoi = ?",
            (user_id, tournament_id)
        ).fetchone()
        is_registered = bool(existing_entry)
    # Affichage de la page principale de l'application
    return render_template('user/profile_edit.html', is_registered=is_registered)

@user_bp.route('/update', methods=['POST'])
@login_required 
def update_profile():
    db = get_db()
    tel = request.form.get('tel')
    mail = request.form.get('mail')
    chesscom = request.form.get('chess_com')
    lichess = request.form.get('lichess')
    sexe = request.form.get('sexe')
    classe = request.form.get('classe')

    if 'photo_de_profil' in request.files:
        file = request.files['photo_de_profil']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)  # Sécuriser le nom du fichier
            UPLOAD_FOLDER = os.path.join(current_app.root_path, 'static', 'imgs','imgs-profil')
            filepath = os.path.join(UPLOAD_FOLDER, filename)  # Définir le chemin
            file.save(filepath)  # Sauvegarder l'image
            photo_de_profil = f"imgs/imgs-profil/{filename}"  # Enregistrer le chemin relatif dans la DB
        else:
            photo_de_profil = g.user['photo_de_profil']  # Garder l'ancienne photo si rien n'est uploadé
    else:
        photo_de_profil = g.user['photo_de_profil']
    try:
        db.execute('''
            UPDATE Utilisateurs
            SET classe= ?, numero_de_telephone = ?, mail = ?, chess_com = ?, lichess = ?, sexe= ?, photo_de_profil= ?
            WHERE id_utilisateurs = ?
        ''', (classe, tel, mail, chesscom, lichess, sexe, photo_de_profil, g.user['id_utilisateurs']))
        db.commit()
        flash("Profil mis à jour avec succès !", "success")
    except Exception as e:
        db.rollback()
        flash(f"Une erreur est survenue : {str(e)}", "error")
    finally:
        close_db()

    return redirect(url_for('user.show_profile'))
