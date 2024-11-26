from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)
from app.utils import *

# Routes /infos/...
infos_bp = Blueprint('infos', __name__, url_prefix='/infos')

# Route /infos/infos 
@infos_bp.route('/infos', methods=('GET', 'POST'))
def show_infos():
    # Affichage de la page des tournois
    return render_template('infos/infos.html')