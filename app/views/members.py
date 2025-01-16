from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)
from app.utils import *
from app.db.db import get_db, close_db

# Routes /members/...
members_bp = Blueprint('members', __name__, url_prefix='/members')

# Route /members/members accessible uniquement à un utilisateur connecté grâce au décorateur @login_required
@members_bp.route('/members', methods=('GET', 'POST'))
@login_required 
def show_members():
    db = get_db()
    admins = db.execute('SELECT * FROM Utilisateurs WHERE role = ?', ('Admin',)).fetchall()
    members = db.execute('SELECT * FROM Utilisateurs WHERE role = ?', ('Membre',)).fetchall()
    close_db()

    # Affichage de la page des membres
    return render_template('members/members.html', admins=admins, members=members)
