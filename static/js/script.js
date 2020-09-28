function openTab(evt, tabName) {
    var i, tabcontent, tablinks;
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
      tabcontent[i].style.display = "none";
    }
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
      tablinks[i].className = tablinks[i].className.replace(" active", "");
    }
    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.className += " active";
  }

// Get the element with id="defaultOpen" and click on it
document.getElementById("defaultOpen").click();

//Objet JSON qui va contenir le nom des sources de données, des couches, leur chemin et leurs paramètres pour chacune des variables
const mesVar = {
  gpkg:
  {
    nomGPKG:
    {},
    layers:
    {},
  },
  dossier:
  {
    chemin:
    {},
    couches:
    {},
  },
  paramètres:
  {
    défauts:"vide",
    perso: "vide",
    filtres: {},
  },
}
// Choix de l'utilisateur pour importer les données à partir d'un dossier ou d'une base de données Geopackage
let
  data = '',
  listeColumns = [],
  valeurChamps = [],
  listeStructuration = [];
  geomType = '';
  result = '';

//Valider le choix de la source de donnée
$(document).ready(function(){
  //Bouton de validation de la source de donnée (Dossier ou GPKG)
  $("#btn-valid").on('click', function(){
    if ($("select.dossier").val() === "dossier"){
        $.ajax({
            type: 'GET',
            url: '/importData/selectionDossier',
            success: function (response) {
                mesVar.dossier.chemin = response;
                data = response;
            }
        })
      $('#selection').html("<img src='/static/images/folder.svg'>");
    }
  else if ($("select.dossier").val() === "BDgpkg"){
      $.ajax({
          type: 'GET',
          url: '/importData/selectionBDgpkg',
          success: function (response) {
              mesVar.gpkg.nomGPKG = response;
              data = response;
          }
      })
      $('#selection').html("<img src='/static/images/database.svg'>");
    }
  })
})
//Fonction qui va lister les données du dossier ou de la BD gpkg
//ET Permettre la sélection de la donnée à attribuer à une variable
let ul = $("ul.data")
//Fonction qui va attribuer la donnée sélectionnée à la variable associée aux boutons
$(document).ready(function(){
  $("#btn-liste").on('click', function(){
      liste = [];
      $('li.donnees').remove();
      $.ajax({
          method: 'POST',
          url: '/importData/liste_data',
          data: {chemin : data},
          success: function (response) {
              liste = response;
              liste.forEach(shp => {
                  $('<li class="donnees"></li>').html(shp).appendTo(ul);
              })
              $('h4#listeCouches').html('Liste des '+liste.length+' couches')
              $('li.donnees').on('click', function(){
                  $(this).siblings().removeClass("classLi");
                  $(this).toggleClass("classLi");
              })
          }
      })
  })
})
// Attribution des données aux variables avec vérification des géométries
$(".group").on('click','.btn-test', function(){
  let select = $(".donnees.classLi").html();
  let divParent = $(this).parent();
  $(divParent).children("span").html(select);
  let iload = $(divParent).children("i")
  let span = $(divParent).children("span");
  let key = $(this).html();
  $('<div class="lds-dual-ring"></div>').appendTo(iload)
  function check(something){
      let
        data1 = ["Parcelles", "Bâti", "Structuration territoriale"].includes(key),
        geomPoly = ['Polygon', 'MultiPolygon'].includes(something),
        condition1 = (data1 && geomPoly === false) ? true : false,
        data2 = ["Routes", "Voies ferrées"].includes(key),
        geomLine = ['LineString', 'MultiString'].includes(something),
        condition2 = (data2 && geomLine === false) ? true : false,
        condition3 = something === 'Couche vide';
      if (something === 'MultiPolygon' || something === 'Polygon') {
        $(divParent).children("i").html("<img src='/static/images/polygon.svg'>")
      }else if (something === 'Points'){
        $(divParent).children("i").html("<img src='/static/images/point.svg'>")
      }else if (something === 'LineString'){
          $(divParent).children("i").html("<img src='/static/images/line.svg'>")
      }
      if (condition1 || condition2){
        alert("La donnée sélectionnée n'as pas la bonne géométrie! Pour les 'Parcelles', le 'Bâti' et la 'Structuration territoriale', veuillez sélectionner une donnée de type Polygon ou MultiPolygon et pour les 'Routes' et les 'Voies ferrées' une donnée de type LineString (ligne)");
        span.css("color", "red");
      } else if (condition3) {
        alert('Cette couche est vide !');
        span.css("color", "red");
      } else {
        span.css("color", "black");
        // if (key === "Structuration territoriale"){
        //     $.ajax({
        //         type:'POST',
        //         url:'/potentiel/structuration_territoriale',
        //         data: {chemin: data, nom: select},
        //         success: function (response) {
        //             listeStructuration = response
        //         }
        //     })
        // }
        if (data.endsWith(".gpkg")){
          delete mesVar.dossier.couches[key];
          mesVar.gpkg.layers[key] = select;
        }else{
          delete mesVar.gpkg.layers[key];
          mesVar.dossier.couches[key] = select;
        }
    }
  }
  $.ajax({
      type: 'POST',
      data: {
          chemin : data,
          layer : select},
      url: '/importData/geometryType',
      success: function (response) {
          console.log(response);
          check(response);
      }
  })
})

//fonction qui va récupérer les paramètres définis pour chaque type de la couche structuration territoriale
function recupDonnees(){
  if(document.querySelector('.on')){
  document.querySelector('.on').addEventListener('click', function() {
    let nomColumn = $("tr.titre th:first-child").html();
    console.log(nomColumn);
    mesVar.paramètres.perso.champs = nomColumn;
    const tr = document.querySelectorAll("tr.donnees");
    for (const item of tr) {
      let nodes = item.querySelectorAll('td');
      let first = nodes[0].innerHTML
      let inputs = item.querySelectorAll('input')
      let value0 = parseInt(inputs[0].value);
      let value1 = parseInt(inputs[1].value);
      let value2 = parseInt(inputs[2].value);
      let value3 = parseInt(inputs[3].value);
      let value4 = parseInt(inputs[4].value);
      //let value5 = parseInt(inputs[5].value);
      mesVar.paramètres.perso.valeurs[first] = {
          //"d_min_route" : value0,
          "non-batie" : value0,
          "batie" : value1,
          "cesMax" : value2,
          "test" : value3,
          "bufBati" : value4,
        }
      };
    mesVar.paramètres.défauts = 'vide';
    console.log(mesVar.paramètres);
    $(".on").css("background-color", "#08bd50");
    })
  }
}
//Fonction qui va remplir le tableau avec les paramètres de la structuration territoriale avec les valeurs par défaut
function valeursTable(liste){
  const container = document.querySelector("#container1");
  //const route = container.querySelector("#route").value;
  const nonBatie = container.querySelector("#non-batie").value;
  const batie = container.querySelector("#batie").value;
  const cesMax = container.querySelector("#cesMax").value;
  const test = container.querySelector("#test").value;
  const bufBati = container.querySelector("#bufBati").value;
  for (const valeur of liste) {
     $('<tr class="donnees" id='+valeur+'><td>'+valeur+'</td><td><input type="number" class="non-batie" value='+nonBatie+'>m</td><td><input type="number" class="batie" value='+batie+'>m</td><td><input type="number" class="cesMax" value='+cesMax+'>m</td><td><input type="number" class="test" value='+test+'>m</td><td><input type="number" class="bufBati" value='+bufBati+'>m</td></tr>').appendTo('#table-env');
  }
}

// Ajout de filtres
$(document).ready(function(){
  $("#btn-addFilter").on('click', function(){
    let filterPlace = $("div#filter");
    let name = prompt("Indiquez le nom du filtre : ");
    $('<div class="group"><button style= "background-color: #8e1f31"  class="btn-test filtre" id='+name+'>'+name+'</button><button class="remove">X</button><i></i><span id="vf-canvas" class="data-info"></span><div class="buffer"><input type="number" value=0><button class="okBuffer">OK</button></div></div>').appendTo(filterPlace.children("div"));
    $(".group").on('click',".btn-test.filtre", function(){
      let select = $(".donnees.classLi").html();
      let divParent = $(this).parent();
      $(divParent).children("span").html(select);
      let key = $(this).html();
      let span = $(divParent).children("span");
      function check(something){
          if (something === 'MultiPolygon' || something === 'Polygon') {
            $(divParent).children("i").html("<img src='/static/images/polygon.svg'>")
          }else if (something === 'Points'){
            $(divParent).children("i").html("<img src='/static/images/point.svg'>")
          }else if (something === 'LineString'){
            $(divParent).children("i").html("<img src='/static/images/line.svg'>")
          }
          if (something === 'Couche vide'){
            alert('Cette couche est vide');
            span.css("color", "red");
          }else {
            span.css("color", "black");
            mesVar.paramètres.filtres[key] = 0;
            if (data.endsWith(".gpkg")){
              delete mesVar.dossier.couches[key];
              mesVar.gpkg.layers[key] = select;
            }else{
              delete mesVar.gpkg.layers[key];
              mesVar.dossier.couches[key] = select;
            }
          }
        }
        $.ajax({
            type: 'POST',
            data: {
                chemin : data,
                layer : select},
            url: '/importData/geometryType',
            success: function (response) {
                check(response);
            }
        })
    })
    //Bouton de suppression de filtre
    $(".group .remove").on('click', function(){
      let parent = $(this).parent();
      nom = $(parent).children(".btn-test").html();
      delete mesVar.gpkg.layers[nom];
      delete mesVar.dossier.couches[nom];
      delete mesVar.paramètres.filtres[nom];
      $(this).parent().remove();
    })
    $("button.okBuffer").on('click', function(){
      let parent = $(this).parent();
      let input = parent.children('input').val();
      let grandParent = parent.parent();
      nom = $(grandParent).children("button.btn-test").html();
      mesVar.paramètres.filtres[nom] = input;
      parent.children('input').css('background-color', '#aaf2b6')
    })
  })
})

$(document).ready(function(){
  $(".btn_import").on('click', function() {
    let entriesDossier = Object.entries(mesVar.dossier.couches);
    let entriesGpkg = Object.entries(mesVar.gpkg.layers);
    let couchesDossier = {};
    let couchesGpkg = {};
    for (const entry of entriesDossier) {
      couchesDossier[entry[0]] = mesVar.dossier.chemin + '/' + entry[1]
    }
    for (const entry of entriesGpkg) {
      couchesGpkg[entry[0]] = mesVar.gpkg.nomGPKG + '*' + entry[1]
    }
    let couches = {
      ...couchesDossier,
      ...couchesGpkg
    }
    $.ajax({
        type: 'POST',
        data: couches,
        url: "/potentiel/import_donnees",
        success: function (response) {
            alert("Les données ont bien été importées, vous pouvez maintenant calculer le potentiel foncier ou l'enveloppe urbaine.");
            $("#btn_import").css("background-color", "#08bd50");
            listeStructuration = response;
        }
    });
  })
})

//PARAMETRES
let ulColumns = $("ul#columns")
$(document).ready(function(){
  $("#valid-param").on("click", function(){
    mesVar.paramètres["défauts"] = {};
    let paramRoute = $("#route").val();
    mesVar.paramètres.défauts["d_min_route"] = paramRoute;
    let paramNonBatie = $("#non-batie").val();
    mesVar.paramètres.défauts["non-batie"] = paramNonBatie;
    let paramBatie = $("#batie").val();
    mesVar.paramètres.défauts["batie"] = paramBatie;
    let paramCES = $("#cesMax").val();
    mesVar.paramètres.défauts["cesMax"] = paramCES;
    let paramTest = $("#test").val();
    mesVar.paramètres.défauts["test"] = paramTest;
    let paramBufBati = $("#bufBati").val();
    mesVar.paramètres.défauts["bufBati"] = paramBufBati;
    mesVar.paramètres.perso = 'vide';
    $(this).css("background-color", "#08bd50");
    $("#param-perso").css("background-color", "#1F3869")
  })
  $(".off").on('click', function(){
    $("ul#columns").empty();
    listeStructuration.forEach(column => {
      $('<li class="columns"></li>').html(column).appendTo(ulColumns);
      })
    $('#param-confirm').css('visibility', 'visible');
    $('.columnChoice').css('visibility', 'visible');
    this.className = 'btn-test on';
    mesVar.paramètres["perso"] = {
      champs : '',
      valeurs : {},
    };
    recupDonnees();
    $('li.columns').on('click', function(){
        $(this).siblings().removeClass("classLi");
        $(this).toggleClass("classLi");
        let selectColumns = $(".columns.classLi").html();
        let structTerr = '';
        if (mesVar.dossier.couches['Structuration territoriale']) {
            structTerr = mesVar.dossier.chemin + '/' + mesVar.dossier.couches['Structuration territoriale'];
        } else {
            structTerr = [mesVar.gpkg.nomGPKG,  mesVar.gpkg.layers['Structuration territoriale']];
        }
        $.ajax({
            type: 'POST',
            data: {
                champs : selectColumns,
                couche : structTerr
            },
            url: '/importData/unique_values',
            success: function (response) {
                valeurChamps = response;
            }
        })
        $('#table-env').empty();
        $('<tr class="titre"><th>'+selectColumns+'</th><th>Surface minimale de la parcelle non bâtie</th><th>Surface minimale de la parcelle bâtie</th><th>CES maximum de la parcelle divisible</th><th>Distance du buffer pour le test</th><th>Distance du buffer autour du bâti</th></tr>').appendTo('#table-env');
    })
  })

  $('#param-confirm').on('click', function(){
    valeursTable(valeurChamps);
  })
})

$(document).ready(function() {
  $('#btn-script').on('click', function() {
    if (mesVar.paramètres['défauts'] === "vide" && mesVar.paramètres['perso'] === "vide") {
      let answer = window.confirm("Vous n'avez pas valider les paramètres! Etes vous sûre de lancer le traitement avec les paramètres par défaut?")
      if (answer) {
          mesVar.paramètres["défauts"] = {};
          let paramRoute = $("#route").val();
          mesVar.paramètres.défauts["d_min_route"] = paramRoute;
          let paramNonBatie = $("#non-batie").val();
          mesVar.paramètres.défauts["non-batie"] = paramNonBatie;
          let paramBatie = $("#batie").val();
          mesVar.paramètres.défauts["batie"] = paramBatie;
          let paramCES = $("#cesMax").val();
          mesVar.paramètres.défauts["cesMax"] = paramCES;
          let paramTest = $("#test").val();
          mesVar.paramètres.défauts["test"] = paramTest;
          let paramBufBati = $("#bufBati").val();
          mesVar.paramètres.défauts["bufBati"] = paramBufBati;
          mesVar.paramètres.perso = 'vide';
          $.ajax({
              type: 'POST',
              data: JSON.stringify(mesVar),
              url: '/potentiel/lancement',
              success: function (response) {
                  console.log(response);
              }
          })
        //eel.lancement(mesVar)()
      }
      else {
        return;
      }
    }
    else {
        $.ajax({
            type: 'POST',
            data: JSON.stringify(mesVar),
            url: '/potentiel/lancement',
            success: function (response) {
                console.log(response);
            }
        })
        //eel.lancement(mesVar)()
    }
  })
})

$(document).ready(function() {
  $("#btn-export").on('click', function() {
    let exportCes = document.getElementById("ces_check").checked
    function avertissement(valeur) {
      console.log(valeur);
      if (valeur === false){
        alert("Données exportées dans le geopackage app_fonciere/data/resultats.gpkg");
        $("#btn-export").css('background-color', '#aaf2b6');
      }else{
        alert("Aucune donnée, veuillez lancer un traitement")
        $("#btn-export").css('background-color', 'red')
      }
    }
    exportResultat(exportCes, avertissement);
  })
})

//ProgressBar
const progressBar = document.getElementsByClassName('progress-bar')[0]
//eel.expose(progress);
function progress(num) {
    const computedStyle = getComputedStyle(progressBar)
    const width = parseFloat(computedStyle.getPropertyValue('--width')) || 0
    const content = computedStyle.getPropertyValue('content')
    progressBar.style.setProperty('--width', width + num)
    //progressBar.style.setProperty('content', nom)
}
// $.ajax({
//     type: 'GET',
//     url: '/progress'
//     success: function (response) {
//         progress(response)
//     }
// })

//VISUALISATION map
let mymap = L.map('mapid').setView([43.947991, 4.80875], 13);
let Esri_WorldImagery = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
	attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
});
let OpenStreetMap_Mapnik = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
	maxZoom: 19,
	attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
});
Esri_WorldImagery.addTo(mymap);
$(document).ready(function() {
  $("#btn-map").on('click', function() {
    setTimeout(function() { mymap.invalidateSize()}, 1);
  })
})
function onMapClick(e) {
    alert("You clicked the map at " + e.latlng);
}
mymap.on('click', onMapClick);
