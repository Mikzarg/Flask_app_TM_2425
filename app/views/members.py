from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)
from app.utils import *

# Routes /user/...
members_bp = Blueprint('members', __name__, url_prefix='/members')

# Route /user/profile accessible uniquement à un utilisateur connecté grâce au décorateur @login_required
@members_bp.route('/members', methods=('GET', 'POST'))
@login_required 
def show_members():
    # Affichage de la page principale de l'application
    return render_template('members/members.html')