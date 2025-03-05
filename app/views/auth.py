from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash
from app.db.db import get_db, close_db
import os

# Création d'un blueprint contenant les routes ayant le préfixe /auth/...
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Route /auth/register
@auth_bp.route('/register', methods=('GET', 'POST'))
def register():

    # Si des données de formulaire sont envoyées vers la route /register (ce qui est le cas lorsque le formulaire d'inscription est envoyé)
    if request.method == 'POST':
        # On récupère les champs 'username' et 'password' de la requête HTTP
        e_mail = request.form['e_mail']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        name = request.form['name']
        first_name = request.form['first_name']
        classe = request.form['classe']
        sexe = request.form['sexe']
        lichess = request.form['lichess']
        chess_com = request.form['chesscom']
        mail = request.form['mail']
        tel = request.form['tel']

        # On récupère la base de donnée
        db = get_db()

        if password != confirm_password:
            flash("Les mots de passe ne correspondent pas.")
            return redirect(url_for("auth.register"))
        # Si le nom d'utilisateur et le mot de passe ont bien une valeur
        # on essaie d'insérer l'utilisateur dans la base de données
        if e_mail and password and name and first_name and classe:
            # Dictionnaire pour stocker les champs et valeurs
            user_data = {
                "e_mail": e_mail,
                "mot_de_passe": generate_password_hash(password),
                "nom": name,
                "prenom": first_name,
                "classe": classe,
                "sexe" : sexe
            }

            # Ajout des champs facultatifs s'ils sont présents
            if lichess:
                user_data["lichess"] = lichess
            if chess_com:
                user_data["chess_com"] = chess_com
            if mail:
                user_data["mail"] = mail
            if tel:
                user_data["numero_de_telephone"] = tel

            # Construction dynamique de la requête SQL
            columns = ", ".join(user_data.keys())
            placeholders = ", ".join("?" for _ in user_data.values())
            values = list(user_data.values())

            try:
                db.execute(f"INSERT INTO Utilisateurs ({columns}) VALUES ({placeholders})", values)
                db.commit()
                close_db()
            except db.IntegrityError:
                error = f"Utilisateur {e_mail} déjà enregistré."
                flash(error)
                return redirect(url_for("auth.register"))

            return redirect(url_for("auth.login"))
        else:
            error = "Nom d'utilisateur ou mot de passe invalide."
            flash(error)
            return redirect(url_for("auth.login"))
    else:
        return render_template('auth/register.html')

# Route /auth/login
@auth_bp.route('/login', methods=('GET', 'POST'))
def login():
    # Si des données de formulaire sont envoyées vers la route /login (ce qui est le cas lorsque le formulaire de login est envoyé)
    if request.method == 'POST':

        # On récupère les champs 'username' et 'password' de la requête HTTP
        e_mail = request.form['e_mail']
        password = request.form['password']

        # On récupère la base de données
        db = get_db()
        
        # On récupère l'utilisateur avec le username spécifié (une contrainte dans la db indique que le nom d'utilisateur est unique)
        # La virgule après username est utilisée pour créer un tuple contenant une valeur unique
        user = db.execute('SELECT * FROM Utilisateurs WHERE e_mail = ?', (e_mail,)).fetchone()

        # On ferme la connexion à la base de données pour éviter les fuites de mémoire
        close_db()

        # Si aucun utilisateur n'est trouve ou si le mot de passe est incorrect
        # on crée une variable error 
        error = None
        if user is None:
            error = "Nom d'utilisateur incorrect."
        elif not check_password_hash(user['mot_de_passe'], password):
            error = "Mot de passe incorrect."
        # S'il n'y pas d'erreur, on ajoute l'id de l'utilisateur dans une variable de session
        # De cette manière, à chaque requête de l'utilisateur, on pourra récupérer l'id dans le cookie session
        if error is None:
            session.clear()
            session['user_id'] = user['id_utilisateurs']
            # On redirige l'utilisateur vers la page principale une fois qu'il s'est connecté
            return redirect("/")
        
        else:
            # En cas d'erreur, on ajoute l'erreur dans la session et on redirige l'utilisateur vers le formulaire de login
            flash(error)
            return redirect(url_for("auth.login"))
    else:
        return render_template('auth/login.html')

# Route /auth/logout
@auth_bp.route('/logout')
def logout():
    # Se déconnecter consiste simplement à supprimer le cookie session
    session.clear()

    # On redirige l'utilisateur vers la page principale une fois qu'il s'est déconnecté
    return redirect("/")


# Fonction automatiquement appelée à chaque requête (avant d'entrer dans la route) sur une route appartenant au blueprint 'auth_bp'
# La fonction permet d'ajouter un attribut 'user' représentant l'utilisateur connecté dans l'objet 'g' 
@auth_bp.before_app_request
def load_logged_in_user():

    # On récupère l'id de l'utilisateur stocké dans le cookie session
    user_id = session.get('user_id')

    # Si l'id de l'utilisateur dans le cookie session est nul, cela signifie que l'utilisateur n'est pas connecté
    # On met donc l'attribut 'user' de l'objet 'g' à None
    if user_id is None:
        g.user = None

    # Si l'id de l'utilisateur dans le cookie session n'est pas nul, on récupère l'utilisateur correspondant et on stocke
    # l'utilisateur comme un attribut de l'objet 'g'
    else:
         # On récupère la base de données et on récupère l'utilisateur correspondant à l'id stocké dans le cookie session
        db = get_db()
        g.user = db.execute('SELECT * FROM Utilisateurs WHERE id_utilisateurs = ?', (user_id,)).fetchone()
        # On ferme la connexion à la base de données pour éviter les fuites de mémoire
        close_db()





