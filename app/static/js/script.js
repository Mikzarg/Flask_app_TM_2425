function changerBoutonSinscrire() {
    var button = document.getElementById("btnConnect");

    // Vérifie si le bouton a déjà été cliqué
    if (button.classList.contains("clicked")) {
        // Réinitialise l'état du bouton
        button.classList.remove("clicked");
        button.innerHTML = '<h3>S\'INSCRIRE</h3>';
    } else {
        // Ajoute l'état "cliqué"
        button.classList.add("clicked");

        // Ajouter du texte ou d'autres boutons à l'intérieur du bouton
        var addedContent = `
            <h3 id="sinscriree">S'INSCRIRE</h3>
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
function changerBoutonListe() {
  var button = document.getElementById("bouton-sinscrire-tournoi");

  // Vérifie si le bouton a déjà été cliqué
  if (button.classList.contains("clicked")) {
      // Réinitialise l'état du bouton
      button.classList.remove("clicked");
      button.innerHTML = '<h3>LISTE DES PARTICIPANTS</h3>';
  } else {
      // Ajoute l'état "cliqué"
      button.classList.add("clicked");

      // Ajouter du texte ou d'autres boutons à l'intérieur du bouton
      var addedContent = `
        <h3 >LISTE DES PARTICIPANTS</h3>
        <table id="tournoi-liste-tableau">
          <tr>
            <th class="th-liste">1. </th>
            <td class="td-liste">Annette Black</td>
          </tr>
          <tr>
            <th class="th-liste">2. </th>
            <td class="td-liste">Jenny Wilson</td>
          </tr>
          <tr>
            <th class="th-liste">3. </th>
            <td class="td-liste">Floyd Miles</td>
          </tr>
          <tr>
            <th class="th-liste">4. </th>
            <td class="td-liste">Arlene McCoy</td>
          </tr>
          <tr>
            <th class="th-liste">5.</th>
            <td class="td-liste">Eleanor Pena</td>
          </tr>
          <tr>
            <th class="th-liste">6.</th>
            <td class="td-liste">Darlene Robertson</td>
          </tr>
          <tr>
            <th class="th-liste">7.</th>
            <td class="td-liste">Dianne Russell</td>
          </tr>
          <tr>
            <th class="th-liste">8.</th>
            <td class="td-liste">Kristin Watson</td>
          </tr>
          <tr>
            <th class="th-liste">9.</th>
            <td class="td-liste">Jerome Bell</td>
          </tr>
          <tr>
            <th class="th-liste">10.</th>
            <td class="td-liste">Leslie Alexander</td>
          </tr>
        </table>
        <img class="fleche" id="fleche-droite" src="{{url_for('static', filename='imgs/right.png')}}" alt="flèche-droite">

      `;
      button.innerHTML = addedContent; // Ajoute les nouveaux éléments dans le bouton
  }
}





