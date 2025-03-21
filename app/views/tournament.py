from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)
from app.db.db import get_db, close_db
from app.utils import *
import sqlite3
from datetime import datetime
import locale


# Routes /tournament/...
tournament_bp = Blueprint('tournament', __name__, url_prefix='/tournament')

# Actualise les valeurs de tournament
@tournament_bp.before_request
def load_tournament():
    db = get_db()
    tournament = db.execute("SELECT * FROM Tournois ORDER BY id_tournoi DESC LIMIT 1").fetchone()
    if tournament:
        g.tournament = tournament
    else:
        g.tournament = None

# Route /tournament/tournament 
@tournament_bp.route('/', methods=['GET', 'POST'])
def show_tournament():
    db = get_db()
    user_id = session.get('user_id')
    tournament_id = g.tournament['id_tournoi'] if g.tournament else None

    participants = db.execute(
        "SELECT u.prenom, u.nom FROM Participe p JOIN Utilisateurs u ON p.FK_utilisateur = u.id_utilisateurs WHERE p.FK_tournoi = ?",
        (tournament_id,)
    ).fetchall()
    # Définit la langue française pour le formatage
    locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")

    # Convertir la chaîne en un objet date
    date_obj = datetime.strptime(g.tournament['date_limite'], "%Y-%m-%d")

    # Formater la date en mots
    date_lisible_limite = date_obj.strftime("%A %d %B %Y")
    date_lisible_limite = date_lisible_limite.capitalize()

    date_obj1 = datetime.strptime(g.tournament['date_tournoi'], "%Y-%m-%d")

    # Formater la date en mots
    date_lisible_tournoi = date_obj1.strftime("%A %d %B %Y")
    date_lisible_tournoi = date_lisible_tournoi.capitalize()

    # Vérifier si l'utilisateur est inscrit
    is_registered = False
    if user_id and tournament_id:
        existing_entry = db.execute(
            "SELECT 1 FROM Participe WHERE FK_utilisateur = ? AND FK_tournoi = ?",
            (user_id, tournament_id)
        ).fetchone()
        is_registered = bool(existing_entry)
    return render_template('tournament/tournament.html', tournament=g.tournament,participants=participants, is_registered=is_registered, date_lisible_limite=date_lisible_limite, date_lisible_tournoi=date_lisible_tournoi)

@tournament_bp.route('/create', methods=('GET', 'POST'))
def show_create_tournament():
    return render_template('tournament/tournament_create.html', tournament=g.tournament)

@tournament_bp.route('/edit', methods=('GET', 'POST'))
def show_edit_tournament():
    return render_template('tournament/tournament_edit.html', tournament=g.tournament)

@tournament_bp.route('/creating', methods=['POST'])
def create_tournament():
    lieu = request.form.get('lieu')
    date = request.form.get('date')
    horaire = request.form.get('horaire')
    rondes = request.form.get('rondes')
    cadence  = request.form.get('cadence')
    arbitre  = request.form.get('arbitre')
    date_limite = request.form.get('date_limite')
    prix_1  = request.form.get('prix_1')
    prix_2  = request.form.get('prix_2')
    prix_3  = request.form.get('prix_3')
    prix_de_participation = request.form.get('prix_de_participation')

    # Vérification : la date limite ne doit pas être après la date du tournoi
    if date_limite > date:
        flash("Erreur : La date limite d'inscription ne peut pas être après la date du tournoi.", "error")
        return redirect(url_for('tournament.show_create_tournament'))
    # Connexion à la base de données
    db = get_db()
    
    # Insérer les données dans la base de données sans spécifier id_tournoi
    db.execute("""
        INSERT INTO Tournois (lieu, date_tournoi, horaire, rondes, cadence, arbitre, date_limite, prix_1, prix_2, prix_3, prix_de_participation)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?)
    """, (lieu, date, horaire, rondes, cadence, arbitre, date_limite, prix_1, prix_2, prix_3, prix_de_participation))

    # Sauvegarder les modifications
    db.commit()

    # Redirection vers la page des tournois
    return redirect(url_for('tournament.show_tournament'))

@tournament_bp.route('/update', methods=['POST'])
def edit_tournament():
    lieu = request.form.get('lieu')
    date = request.form.get('date')
    horaire = request.form.get('horaire')
    rondes = request.form.get('rondes')
    cadence  = request.form.get('cadence')
    arbitre  = request.form.get('arbitre')
    date_limite = request.form.get('date_limite')
    prix_1  = request.form.get('prix_1')
    prix_2  = request.form.get('prix_2')
    prix_3  = request.form.get('prix_3')
    prix_de_participation  = request.form.get('prix_de_participation')

    # Vérification : la date limite ne doit pas être après la date du tournoi
    if date_limite > date:
        flash("Erreur : La date limite d'inscription ne peut pas être après la date du tournoi.", "error")
        return redirect(url_for('tournament.show_edit_tournament'))
    
    db = get_db()

    try:
        db.execute('''
            UPDATE Tournois
            SET  lieu = ?, date_tournoi = ?, horaire = ?, rondes= ?, cadence = ?, arbitre= ?, date_limite= ?, prix_1= ?, prix_2= ?, prix_3= ?, prix_de_participation= ?
            WHERE id_tournoi = ?
        ''', (lieu, date, horaire, rondes, cadence, arbitre, date_limite, prix_1, prix_2, prix_3, prix_de_participation, g.tournament['id_tournoi']))
        db.commit()
        flash("Tournoi mis à jour avec succès !", "success")
    except Exception as e:
        db.rollback()
        flash(f"Une erreur est survenue : {str(e)}", "error")
    finally:
        close_db()
    return redirect(url_for('tournament.show_tournament'))

@tournament_bp.route('/register', methods=['POST'])
def register_tournament():
    user_id = session.get('user_id') 
    tournament_id = g.tournament['id_tournoi']
    db = get_db()

    # Vérifier si l'utilisateur est déjà inscrit
    existing_entry = db.execute(
        "SELECT * FROM Participe WHERE FK_utilisateur = ? AND FK_tournoi = ?",
        (user_id, tournament_id)
    ).fetchone()
    # Récupérer la date limite du tournoi
    date_limite_str = g.tournament['date_limite']  # Assurez-vous que c'est une chaîne au format "YYYY-MM-DD"
    date_limite = datetime.strptime(date_limite_str, "%Y-%m-%d").date()

    # Récupérer la date actuelle
    date_actuelle = datetime.now().date()

    # Vérifier si la date actuelle est au-delà de la date limite
    if date_actuelle > date_limite:
        flash("Les inscriptions pour ce tournoi sont closes.", "warning")
        return redirect(url_for('tournament.show_tournament'))

    if existing_entry:
        flash("Vous êtes déjà inscrit à ce tournoi.", "warning")
    else:
        db.execute(
            "INSERT INTO Participe (FK_utilisateur, FK_tournoi, points_obtenus, place_au_classement) VALUES (?, ?, 0, NULL)",
            (user_id, tournament_id)
        )
        db.commit()
        flash("Inscription réussie !", "success")
    return redirect(url_for('tournament.show_tournament'))

@tournament_bp.route('/unregister_tournament', methods=['POST'])
def unregister_tournament():
    user_id = session.get('user_id')
    tournament_id = g.tournament['id_tournoi']

    if user_id and tournament_id:
        db = get_db()  # Récupère la connexion à la base de données SQLite
        cursor = db.cursor()

        # Vérifie si l'utilisateur est inscrit à ce tournoi
        cursor.execute('SELECT * FROM Participe WHERE FK_utilisateur = ? AND FK_tournoi = ?', (user_id, tournament_id))
        participation = cursor.fetchone()

        if participation:
            # Si l'utilisateur est inscrit, on le supprime
            cursor.execute('DELETE FROM Participe WHERE FK_utilisateur = ? AND FK_tournoi = ?', (user_id, tournament_id))
            db.commit()  # Commit les changements

            # Redirige vers la page du tournoi après désinscription
            return redirect(url_for('tournament.show_tournament', tournament_id=tournament_id))
        else:
            return redirect(url_for('error_page'))  # L'utilisateur n'est pas inscrit
    else:
        return redirect(url_for('error_page'))  # Pas de session ou tournoi trouvé


# --------- Precedants -----------

@tournament_bp.route('/precedents', methods=('GET', 'POST'))
def show_precedents():
    # Affichage de la page des tournois précédents
    return render_template('tournament/precedents.html')