from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)
from app.utils import *
from app.db.db import get_db, close_db

# Routes /members/...
members_bp = Blueprint('members', __name__, url_prefix='/members')

# Route /members/members accessible uniquement à un utilisateur connecté grâce au décorateur @login_required
@members_bp.route('/', methods=('GET', 'POST'))
@login_required 
def show_members():
    db = get_db()
    admins = db.execute('SELECT * FROM Utilisateurs WHERE role = ?', ('Admin',)).fetchall()
    members = db.execute('SELECT * FROM Utilisateurs WHERE role = ?', ('Membre',)).fetchall()
    last_tournament = db.execute('SELECT * FROM Tournois ORDER BY date_tournoi DESC LIMIT 1').fetchone()

    # Convertir les résultats en listes de dictionnaires
    admins = [dict(admin) for admin in admins]
    members = [dict(member) for member in members]
    last_tournament = dict(last_tournament) if last_tournament else None

    all_users = admins + members
    user_tournaments = {}

    for user in all_users:
        user_id = user['id_utilisateurs']
        tournaments = db.execute('''
        SELECT 
            T.id_tournoi,
            T.date_tournoi,
            P.place_au_classement,
            P.points_obtenus,
            P.FK_utilisateur,
            P.FK_tournoi,
            STRFTIME('%Y', T.date_tournoi) AS annee_tournoi
        FROM Tournois T
        JOIN Participe P ON T.id_tournoi = P.FK_tournoi
        WHERE P.FK_utilisateur = ?
        ORDER BY T.date_tournoi DESC
        ''', (user_id,)).fetchall()

        # Convertir les tournois en dictionnaires
        tournaments = [dict(tournament) for tournament in tournaments]

        # Exclure le dernier tournoi existant
        if tournaments and last_tournament:
            user_tournaments[user_id] = [tournament for tournament in tournaments if tournament['id_tournoi'] != last_tournament['id_tournoi']]
        else:
            user_tournaments[user_id] = []

    close_db()

    return render_template('members/members.html', admins=admins, members=members, user_tournaments=user_tournaments)
