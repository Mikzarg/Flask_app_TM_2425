from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)
from app.utils import *

# Routes /tournament/...
tournament_bp = Blueprint('tournament', __name__, url_prefix='/tournament')

# Route /tournament/tournament 
@tournament_bp.route('/tournament', methods=('GET', 'POST'))
def show_tournament():
    # Affichage de la page des tournois
    return render_template('tournament/tournament.html')