function changerBouton() {
    var button = document.getElementById("btnConnect");

    // Vérifie si le bouton a déjà été cliqué
    if (button.classList.contains("clicked")) {
        // Réinitialise l'état du bouton
        button.classList.remove("clicked");
        button.innerHTML = '<h3 id="sinscrire">S\'INSCRIRE</h3>';
    } else {
        // Ajoute l'état "cliqué"
        button.classList.add("clicked");

        // Ajouter du texte ou d'autres boutons à l'intérieur du bouton
        var addedContent = `
            <h3 id="sinscrire">S'INSCRIRE</h3>
            <p id="text-test">Souhaitez-vous participer au <br>Tournoi d’échecs CSUD 2024?</p>
            <div id="div-test">
              <button class="bouton-test" id="bouton-test-confirmer" onclick="alert('Premier bouton cliqué!')">
                <img class="image-logo" src="{{url_for('static', filename='imgs/vu.png')}}" alt="vu">
                <span>CONFIRMER</span>
              </button>
              <button class="bouton-test" id="bouton-test-annuler" onclick="alert('Deuxième bouton cliqué!')">
                <img class="image-logo" src="{{url_for('static', filename='imgs/croix.png')}}" alt="croix">
                <span>ANNULER</span>
              </button>
            </div>
        `;
        button.innerHTML = addedContent; // Ajoute les nouveaux éléments dans le bouton
    }
}