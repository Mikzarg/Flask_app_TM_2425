from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)
from app.utils import *

# Routes /members/...
members_bp = Blueprint('members', __name__, url_prefix='/members')

# Route /members/members accessible uniquement à un utilisateur connecté grâce au décorateur @login_required
@members_bp.route('/members', methods=('GET', 'POST'))
@login_required 
def show_members():
    # Affichage de la page des membres
    return render_template('members/members.html')