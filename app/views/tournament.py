from flask import (Flask, Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app)
from app.db.db import get_db, close_db
from app.utils import *
import sqlite3
from datetime import datetime
import locale

import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Définition des dossiers d'upload
UPLOAD_FOLDER = 'static/imgs/'  # Dossier principal
CLASS_FOLDER = os.path.join(UPLOAD_FOLDER, 'imgs-classement')  # Dossier pour classement
GALLERY_FOLDER = os.path.join(UPLOAD_FOLDER, 'imgs-galerie')  # Dossier pour galerie

# Assurez-vous que ces dossiers existent
os.makedirs(CLASS_FOLDER, exist_ok=True)
os.makedirs(GALLERY_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

@tournament_bp.route('/', methods=['GET', 'POST'])
def show_tournament():
    db = get_db()
    user_id = session.get('user_id')
    tournament_id = g.tournament['id_tournoi'] if g.tournament else None
    if g.tournament:
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

        date_limite = g.tournament['date_limite']
        date_actuelle = datetime.now()
        inscriptions_fermees = date_actuelle > datetime.strptime(date_limite, "%Y-%m-%d")
        return render_template('tournament/tournament.html', tournament=g.tournament,participants=participants, is_registered=is_registered, date_lisible_limite=date_lisible_limite, date_lisible_tournoi=date_lisible_tournoi, inscriptions_fermees=inscriptions_fermees)
    else:
        flash("Aucun tournoi en cours.", "warning")
        return render_template('tournament/tournament.html', tournament=None)

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
    if not g.tournament:
        flash("Erreur : Aucun tournoi en cours à modifier.", "error")
        return redirect(url_for('tournament.show_tournament'))

    lieu = request.form.get('lieu')
    date = request.form.get('date')
    horaire = request.form.get('horaire')
    rondes = request.form.get('rondes')
    cadence = request.form.get('cadence')
    arbitre = request.form.get('arbitre')
    date_limite = request.form.get('date_limite')
    prix_1 = request.form.get('prix_1')
    prix_2 = request.form.get('prix_2')
    prix_3 = request.form.get('prix_3')
    prix_de_participation = request.form.get('prix_de_participation')

    # Vérification : la date limite ne doit pas être après la date du tournoi
    if date_limite > date:
        flash("Erreur : La date limite d'inscription ne peut pas être après la date du tournoi.", "error")
        return redirect(url_for('tournament.show_edit_tournament'))
    
    db = get_db()

    try:
        db.execute('''
            UPDATE Tournois
            SET lieu = ?, date_tournoi = ?, horaire = ?, rondes = ?, cadence = ?, arbitre = ?, 
                date_limite = ?, prix_1 = ?, prix_2 = ?, prix_3 = ?, prix_de_participation = ?
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
    db = get_db()  
    db.execute(
        'DELETE FROM Participe WHERE FK_utilisateur = ? AND FK_tournoi = ?', 
        (user_id, tournament_id))
    db.commit()  
    return redirect(url_for('tournament.show_tournament', tournament_id=tournament_id))


# --------- Precedents -----------

@tournament_bp.route('/precedents', methods=['GET'])
def show_precedents():
    db = get_db()
    
    # Trouver l'ID du dernier tournoi en date
    dernier_tournoi = db.execute(
        "SELECT id_tournoi FROM Tournois ORDER BY date_tournoi DESC LIMIT 1"
    ).fetchone()

    id_dernier = dernier_tournoi['id_tournoi'] if dernier_tournoi else None

    # Construire la requête SQL de manière conditionnelle
    if id_dernier:
        query = """
        SELECT Tournois.id_tournoi, Tournois.date_tournoi, Photos.description, Photos.chemin_vers_la_photo, Photos.id_photos, Photos.type_photo
        FROM Tournois
        LEFT JOIN Photos ON Tournois.id_tournoi = Photos.id_tournoi
        WHERE Tournois.id_tournoi != ?
        ORDER BY Tournois.date_tournoi DESC
        """
        params = (id_dernier,)
    else:
        query = """
        SELECT Tournois.id_tournoi, Tournois.date_tournoi, Photos.description, Photos.chemin_vers_la_photo, Photos.id_photos, Photos.type_photo
        FROM Tournois
        LEFT JOIN Photos ON Tournois.id_tournoi = Photos.id_tournoi
        ORDER BY Tournois.date_tournoi DESC
        """
        params = ()

    tournois = db.execute(query, params).fetchall()

    # Construction du dictionnaire des tournois
    tournois_dict = {}

    for tournoi in tournois:
        annee = datetime.strptime(tournoi['date_tournoi'], '%Y-%m-%d').year

        if annee not in tournois_dict:
            tournois_dict[annee] = {
                'id_tournoi': tournoi['id_tournoi'],
                'photos_classement': [],  
                'photos_galerie': []     
            }

        if tournoi['type_photo'] == 'classement':
            tournois_dict[annee]['photos_classement'].append({
                'id_photo': tournoi['id_photos'],
                'chemin_vers_la_photo': tournoi['chemin_vers_la_photo'],
                'description': tournoi['description']
            })
        elif tournoi['type_photo'] == 'galerie':
            tournois_dict[annee]['photos_galerie'].append({
                'id_photo': tournoi['id_photos'],
                'chemin_vers_la_photo': tournoi['chemin_vers_la_photo'],
                'description': tournoi['description']
            })
    dates_tournois = db.execute("""
        SELECT date_tournoi
        FROM Tournois
        WHERE id_tournoi != (SELECT id_tournoi FROM Tournois ORDER BY date_tournoi DESC LIMIT 1)
        ORDER BY date_tournoi DESC
    """).fetchall()
    return render_template('tournament/precedents.html', tournois=tournois_dict, dates_tournois=dates_tournois)


@tournament_bp.route('/precedents/add', methods=['GET'])
def show_add_precedents():
    db = get_db()

    # Récupérer les dates complètes des tournois précédents (sauf le dernier)
    query = """
    SELECT date_tournoi
    FROM Tournois
    WHERE id_tournoi != (SELECT id_tournoi FROM Tournois ORDER BY date_tournoi DESC LIMIT 1)
    ORDER BY date_tournoi DESC
    """
    
    tournois = db.execute(query).fetchall()

    dates_tournois = [tournoi['date_tournoi'] for tournoi in tournois]

    return render_template('tournament/precedents_add.html',dates_tournois=dates_tournois)

@tournament_bp.route('/precedents/adding', methods=['POST'])
def add_precedents():
    annee = request.form['annee']
    type_photo = request.form['type'] 
    description = request.form['description']

    db = get_db()
    
    tournoi = db.execute('''
            SELECT id_tournoi FROM Tournois WHERE date_tournoi = ?
            ''', (annee,)).fetchone()
    
    if not tournoi:
        flash("Aucun tournoi trouvé pour cette année.", "error")
        return redirect(url_for('tournament.show_add_precedents')) 

    tournoi_id = tournoi['id_tournoi']

    photo = None
    file = request.files.get('photo')  
    if file is None or file.filename == '':
        flash("Veuillez sélectionner une image avant de continuer !", "error")
        return redirect(url_for('tournament.show_add_precedents'))  

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)

        folder = 'imgs-classement' if type_photo == 'classement' else 'imgs-galerie'
        upload_folder = os.path.join(current_app.root_path, 'static', 'imgs', folder)

        os.makedirs(upload_folder, exist_ok=True)

        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)

        photo = f"imgs/{folder}/{filename}"
    else:
        flash("Le fichier choisi n'est pas valide. Veuillez sélectionner une image valide.", "error")
        return redirect(url_for('tournament.show_add_precedents'))  

    try:
        db.execute('''
            INSERT INTO Photos (id_tournoi, type_photo, description, chemin_vers_la_photo)
            VALUES (?, ?, ?, ?)
        ''', (tournoi_id, type_photo, description, photo))

        db.commit()  
        flash("Photo ajoutée avec succès !", "success")  
    except Exception as e:
        db.rollback()  
        flash(f"Une erreur est survenue : {str(e)}", "error")  
    finally:
        close_db()  

    return redirect(url_for('tournament.show_add_precedents'))




