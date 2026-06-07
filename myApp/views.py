from flask import Flask, render_template, request, redirect, session, flash, url_for
import mysql.connector
import secrets
import string
import hashlib
from myApp.config import DB_SERVER
import myApp.controller.function as f
import myApp.model.bdd as bdd

app = Flask(__name__)
app.template_folder = "template"
app.static_folder = "static"
app.layout_folder = "layout"
app.config.from_object("myApp.config")


def get_db_connection():
    return mysql.connector.connect(**DB_SERVER)


def get_flashcard_banks():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT c.idcategorie AS id,
               c.nomcategorie AS name,
               COUNT(carte.idcarte) AS card_count
        FROM categorie c
        LEFT JOIN paquet p ON p.idcategorie = c.idcategorie
        LEFT JOIN carte ON carte.idpaquet = p.idpaquet
        GROUP BY c.idcategorie, c.nomcategorie
        ORDER BY c.nomcategorie
        """
    )
    banks = cursor.fetchall()
    cursor.close()
    conn.close()
    return banks


def get_flashcards_by_bank(bank_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT carte.idcarte AS id,
               carte.question,
               carte.reponse,
               p.nompaquet AS pack_name,
               cat.nomcategorie AS category_name
        FROM carte
        INNER JOIN paquet p ON p.idpaquet = carte.idpaquet
        INNER JOIN categorie cat ON cat.idcategorie = p.idcategorie
        WHERE cat.idcategorie = %s
        ORDER BY p.nompaquet, carte.idcarte
        """,
        (bank_id,)
    )
    cards = cursor.fetchall()
    cursor.close()
    conn.close()
    return cards


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/team/camille")
def team_camille():
    return render_template("team/camille.html")

@app.route("/team/etienne")
def team_etienne():
    return render_template("team/etienne.html")

@app.route("/team/luka")
def team_luka():
    return render_template("team/luka.html")

@app.route("/team/darya")
def team_darya():
    return render_template("team/darya.html")


@app.route("/signin", methods=["GET", "POST"])
def signin():
    return render_template("signin.html")

@app.route("/connecter", methods=["GET", "POST"])
def connect():
    if request.method == "POST":
        login = request.form['login'].strip()
        mdp = request.form['mdp']
        user = bdd.verifAuthData(login, mdp)
        if not user:
            flash("Identifiants incorrects", "danger")
            return redirect("/signin")
        session["idUser"] = user["idutilisateur"]
        session["idutilisateur"] = user["idutilisateur"]
        session["nom"] = user["nom"]
        session["prenom"] = user["prenom"]
        session["mail"] = user["mail"]
        session["pseudo"] = user["pseudo"]
        session["statut"] = user["statut"]
        flash("Authentification réussie", "success")
        if session["statut"] == "administrateur":
            return redirect("/admin")
        if session["statut"] == "gestionnaire":
            return redirect("/gestion")
        return redirect("/banques")
    return render_template("signin.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Vous avez été déconnecté", "success")
    return redirect("/signin")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        rform = request.form
        if bdd.check_email(rform["email"]):
            flash("Cette adresse mail est déjà utilisée", "danger")
            return redirect(url_for('signup'))
        if bdd.check_pseudo(rform["pseudo"]):
            flash("Ce pseudonyme est déjà utilisé", "danger")
            return redirect(url_for('signup'))
        caracteres = string.ascii_letters + string.digits
        mdp = ''.join(secrets.choice(caracteres) for _ in range(5))
        mdp_hash = hashlib.sha256(mdp.encode()).hexdigest()
        msg = {
            "ok": "Vos informations ont bien été ajoutées à la base de données, veuillez à présent choisir un nouveau mot de passe.",
            "echec": "Echec d'ajout des informations dans la base de données"
        }
        idutilisateur = bdd.add_userData(rform, mdp_hash, msg)
        if idutilisateur:
            user = bdd.get_userById(idutilisateur)
            if user:
                session["idUser"] = idutilisateur
                session["idutilisateur"] = idutilisateur
                session["nom"] = user["nom"]
                session["prenom"] = user["prenom"]
                session["mail"] = user["mail"]
                session["pseudo"] = user["pseudo"]
                session["statut"] = user["statut"]
            flash(f"Votre mot de passe actuel est : {mdp}", "info")
            return redirect(url_for('modifMdp'))
        flash("Une erreur s'est produite lors de l'inscription, veuillez réessayer", "danger")
        return redirect(url_for('signup'))
    return render_template("signup.html")


@app.route("/modifMdp", methods=['GET', 'POST'])
def modifMdp():
    idutilisateur = session.get('idUser') or session.get('idutilisateur')
    if not idutilisateur:
        flash("Veuillez vous connecter pour modifier votre mot de passe", "danger")
        return redirect(url_for('signin'))
    if request.method == 'POST':
        ancien_mdp = request.form.get('ancienmdp')
        nv_mdp = request.form.get('nvmdp')
        confirm_mdp = request.form.get('confirmmdp')
        if hashlib.sha256(ancien_mdp.encode()).hexdigest() != bdd.getMdp(idutilisateur):
            flash("Le mot de passe saisi dans Ancien mot de passe ne correspond pas", "danger")
            return redirect(url_for('modifMdp'))
        if nv_mdp != confirm_mdp:
            flash("Les mots de passe saisis dans Nouveau mot de passe et Confirmer votre nouveau mot de passe ne correspondent pas", "danger")
            return redirect(url_for('modifMdp'))
        if len(nv_mdp) < 8:
            flash("Votre nouveau mot de passe doit contenir au moins 8 caractères", "danger")
            return redirect(url_for('modifMdp'))
        nv_mdp_hash = hashlib.sha256(nv_mdp.encode()).hexdigest()
        bdd.update_userMdpData(nv_mdp_hash, idutilisateur)
        flash("Votre mot de passe a bien été modifié.", "success")
        return redirect(url_for('signin'))
    return render_template("modifMdp.html")


@app.route("/banques")
@f.statuts_obligatoires()
def banques():
    error = None
    banks = []
    try:
        banks = get_flashcard_banks()
    except Exception:
        error = "Impossible de charger les banques de flashcards pour le moment."
    return render_template("banques.html", banks=banks, error=error)

@app.route("/banques/<int:bank_id>")
@f.statuts_obligatoires()
def banque_detail(bank_id):
    error = None
    banks = []
    cards = []
    selected_bank = None
    try:
        banks = get_flashcard_banks()
        selected_bank = next((bank for bank in banks if bank["id"] == bank_id), None)
        cards = get_flashcards_by_bank(bank_id)
    except Exception:
        error = "Impossible d'afficher cette banque pour le moment."
    return render_template(
        "banques.html",
        banks=banks,
        cards=cards,
        selected_bank=selected_bank,
        error=error,
    )

@app.route("/admin")
@f.statuts_obligatoires('administrateur')
def admin():
    listMember = bdd.get_membresData()
    params = {'liste': listMember}
    return render_template("admin.html", **params)

@app.route("/gestion")
@f.statuts_obligatoires('gestionnaire', 'administrateur')
def gestion():
    iduser = session.get("idutilisateur")
    nbcartes = bdd.get_nombrecartes_user(iduser)
    list_paquet = bdd.get_liste_iduser(iduser)
    nb_cartes_maitrisees = bdd.get_nb_cartes_maitrisees(iduser)['nb_cartes_maitrisees']
    nb_cartes = bdd.nb_cartes(iduser)['nb_cartes']
    nb_paquets = bdd.get_nb_paquets(iduser)["nb_paquets"]
    if nb_cartes == 0:
        p_cartes_maitrisees = "Aucune carte à réviser"
    else:
        p_cartes_maitrisees = f"{nb_cartes_maitrisees/nb_cartes*100:.3g} %"
    nb_cartes_par_boite = {}
    nb_cartes_a_reviser_par_boite = {}
    nb_cartes_a_reviser = 0
    for d in bdd.get_idboite():
        idboite = d["idboite"]
        if idboite == 0:
            nb_cartes_par_boite["Cartes maîtrisées"] = bdd.get_nb_cartes_par_boite(iduser, idboite)["nb_cartes_par_boite"]
        else:
            nb_cartes_par_boite[f"Boîte {idboite}"] = bdd.get_nb_cartes_par_boite(iduser, idboite)["nb_cartes_par_boite"]
            tmp = bdd.get_nb_cartes_a_reviser_par_boite(iduser, idboite)
            if tmp is not None:
                nb_cartes_a_reviser_par_boite[f"Boîte {idboite}"] = tmp["nb_cartes_a_reviser_par_boite"]
                nb_cartes_a_reviser += nb_cartes_a_reviser_par_boite[f"Boîte {idboite}"]
    param = {
        'nbcartes': nbcartes,
        'liste': list_paquet,
        "p_cartes_maitrisees": p_cartes_maitrisees,
        "nb_cartes_par_boite": nb_cartes_par_boite,
        "nb_cartes_a_reviser_par_boite": nb_cartes_a_reviser_par_boite,
        "nb_cartes": nb_cartes,
        "nb_paquets": nb_paquets,
        "nb_cartes_a_reviser": nb_cartes_a_reviser
    }
    return render_template("gestion.html", **param)

@app.route("/delete_user/<idutilisateur>")
@f.statuts_obligatoires('administrateur')
def delete_user(idutilisateur):
    msg = {
        "ok": "L'utilisateur a bien été supprimé de la base de données.",
        "echec": "Echec de suppression de l'utilisateur dans la base de données"
    }
    bdd.delete_userData(idutilisateur, msg)
    return redirect(url_for('admin'))


@app.route("/categorie")
@f.statuts_obligatoires('administrateur')
def categorie():
    listCategory = bdd.get_categories()
    params = {'liste': listCategory}
    return render_template("categorie.html", **params)

@app.route("/categorie/choix")
@f.statuts_obligatoires('administrateur')
def choix_categorie():
    categories = bdd.get_categories()
    return render_template("categorie/choix.html", categories=categories)

@app.route("/categorie/creation", methods=["GET", "POST"])
def creation_categorie():
    if request.method == "POST":
        nomcategorie = request.form.get("nomcategorie")
        msg = {
            "ok": "La catégorie a bien été ajoutée à la base de données.",
            "echec": "Echec de l'ajout de la catégorie à la base de données"
        }
        if bdd.check_category_name(nomcategorie):
            flash("Ce nom de catégorie est déjà utilisé", "danger")
            categories = bdd.get_categories()
            return render_template("categorie/choix.html", categories=categories)
        bdd.create_category(nomcategorie, msg)
        categories = bdd.get_categories()
        return render_template("categorie/choix.html", categories=categories)
    return render_template("/categorie/creation.html")

@app.route("/categorie/supprimer/<idcategorie>")
@f.statuts_obligatoires('administrateur')
def delete_category(idcategorie):
    msg = {
        "ok": "La catégorie a bien été supprimée de la base de données.",
        "echec": "Echec de suppression de la catégorie dans la base de données"
    }
    bdd.delete_category(idcategorie, msg)
    categories = bdd.get_categories()
    return render_template("categorie/choix.html", categories=categories)

@app.route("/categorie/renommer/<idcategorie>", methods=["GET", "POST"])
@f.statuts_obligatoires('administrateur')
def rename_category(idcategorie):
    if request.method == "POST":
        nomcategorie = request.form.get("nomcategorie")
        msg = {
            "ok": "La catégorie a bien été renommée.",
            "echec": "Echec du renommage de la catégorie."
        }
        if bdd.check_category_name(nomcategorie):
            flash("Ce nom de catégorie est déjà utilisé", "danger")
            categories = bdd.get_categories()
            return render_template("categorie/choix.html", categories=categories)
        bdd.rename_category(idcategorie, nomcategorie, msg)
        categories = bdd.get_categories()
        return render_template("categorie/choix.html", categories=categories)
    return render_template("categorie/modif.html", categorie=categorie)


@app.route("/paquet")
@f.statuts_obligatoires()
def paquet():
    return render_template("paquet.html")

@app.route("/paquet/choix")
def choix_paquet():
    iduser = session.get("idutilisateur")
    paquets = bdd.get_paquets_user(iduser)
    if not paquets:
        paquets = []
    return render_template("paquet/choix.html", paquets=paquets)

@app.route("/paquet/creation", methods=["GET", "POST"])
def creation_paquet():
    if request.method == "POST":
        nompaquet = request.form.get("nom_paquet")
        idcreateur = session.get("idutilisateur")
        idcategorie = request.form.get("categorie")
        public = 1 if request.form.get("public") else 0
        bdd.create_paquet(nompaquet, idcreateur, public, int(idcategorie))
        return redirect("/paquet/choix")
    categories = bdd.get_categories()
    return render_template("/paquet/creation.html", categories=categories)

@app.route("/paquet/supprimer/<int:idpaquet>")
def supprimer_paquet(idpaquet):
    idcreateur = session.get("idutilisateur")
    bdd.delete_paquet(idpaquet, idcreateur)
    return redirect("/paquet/choix")

@app.route("/paquet/modifier/<int:idpaquet>", methods=["GET", "POST"])
def modifier_paquet(idpaquet):
    iduser = session.get("idutilisateur")
    paquet = bdd.get_one_paquet(idpaquet, iduser)
    if request.method == "POST":
        nom = request.form.get("nom_paquet")
        idcategorie = request.form.get("categorie")
        public = request.form.get("public")
        public = 1 if public else 0
        bdd.update_paquet(idpaquet, nom, public, int(idcategorie))
        return redirect("/paquet/choix")
    categories = bdd.get_categories()
    categories = sorted(categories, key=lambda c: c['idcategorie'] != paquet['idcategorie'])
    return render_template("paquet/modif.html", paquet=paquet, categories=categories)

@app.route("/updatecarte")
@f.statuts_obligatoires()
def updatecarte():
    return render_template("creationcartes.html")

@app.route("/listepaquet")
@f.statuts_obligatoires()
def listepaquet():
    list_paquet = bdd.get_liste_public()
    categories = get_flashcard_banks()
    params = {'liste': list_paquet, 'categories': categories}
    return render_template("listepaquet.html", **params)

@app.route("/paquet/copier/<int:idpaquet>")
@f.statuts_obligatoires()
def copier_paquet_public(idpaquet):
    iduser = session.get("idutilisateur")
    nouveau_idpaquet = bdd.copy_public_paquet(idpaquet, iduser)
    if nouveau_idpaquet:
        flash("Le paquet public a été copié dans votre espace personnel.", "success")
        return redirect(url_for("choix_paquet"))
    flash("Impossible de copier ce paquet public.", "danger")
    return redirect(url_for("listepaquet"))

@app.route("/cartes/<int:idpaquet>")
@f.statuts_obligatoires()
def cartes(idpaquet):
    cartes = bdd.get_cartes_by_paquet(idpaquet)
    return render_template("paquet/cartes.html", cartes=cartes, idpaquet=idpaquet)

@app.route("/cartes/<int:idpaquet>/ajouter", methods=["GET", "POST"])
@f.statuts_obligatoires()
def ajouter_carte(idpaquet):
    if request.method == "POST":
        question = request.form["question"]
        reponse = request.form["reponse"]
        msg = {
            "ok": "Carte ajoutée avec succès !",
            "echec": "Erreur lors de l'ajout de la carte"
        }
        bdd.add_carte(question, reponse, idpaquet, msg)
        return redirect(url_for('cartes', idpaquet=idpaquet))
    return render_template("paquet/creationcartes.html", idpaquet=idpaquet, carte=None)

@app.route("/cartes/modifier/<int:idcarte>", methods=["GET", "POST"])
@f.statuts_obligatoires()
def modifier_carte(idcarte):
    carte = bdd.get_carte_by_id(idcarte)
    if request.method == "POST":
        question = request.form["question"]
        reponse = request.form["reponse"]
        msg = {
            "ok": "Carte modifiée avec succès !",
            "echec": "Erreur lors de la modification de la carte"
        }
        bdd.update_carte(idcarte, question, reponse, msg)
        return redirect(url_for('cartes', idpaquet=carte['idpaquet']))
    return render_template("paquet/creationcartes.html", idpaquet=carte['idpaquet'], carte=carte)

@app.route("/cartes/supprimer/<int:idcarte>")
@f.statuts_obligatoires()
def supprimer_carte(idcarte):
    carte = bdd.get_carte_by_id(idcarte)
    idpaquet = carte['idpaquet']
    msg = {
        "ok": "Carte supprimée avec succès !",
        "echec": "Erreur lors de la suppression de la carte"
    }
    bdd.delete_carte(idcarte, msg)
    return redirect(url_for('cartes', idpaquet=idpaquet))


@app.route("/revision")
@f.statuts_obligatoires()
def revision():
    return render_template("revision.html")

@app.route("/revision/choix")
@f.statuts_obligatoires()
def choix_revision():
    iduser = session.get("idutilisateur")
    paquets = bdd.get_paquets_revision(iduser)
    categories = {}
    for paquet in paquets:
        categorie = paquet["nomcategorie"]
        if categorie not in categories:
            categories[categorie] = []
        categories[categorie].append(paquet)
    return render_template("revision/choix.html", categories=categories)

@app.route("/revision/<int:idpaquet>")
@f.statuts_obligatoires()
def revision_paquet(idpaquet):
    idutilisateur = session.get("idutilisateur")
    cartes = bdd.get_cartes_a_reviser(idutilisateur, idpaquet)
    if not cartes:
        flash("Aucune carte à réviser pour le moment !", "info")
        return redirect(url_for("choix_revision"))
    session["revision_paquet"] = idpaquet
    session["revision_index"] = 0
    session["show_answer"] = False
    session["revision_carte_ids"] = [c["idcarte"] for c in cartes]
    return redirect(url_for("revision_carte"))

@app.route("/revision/carte")
@f.statuts_obligatoires()
def revision_carte():
    carte_ids = session.get("revision_carte_ids")
    if not carte_ids:
        return redirect(url_for("choix_revision"))
    index = session.get("revision_index", 0)
    if index >= len(carte_ids):
        return render_template("revision/fin.html")
    carte = bdd.get_carte_by_id(carte_ids[index])
    return render_template("revision/revision_paquet.html", carte=carte,
                           show_answer=session.get("show_answer", False))

@app.route("/revision/reponse", methods=["POST"])
@f.statuts_obligatoires()
def afficher_reponse():
    session["show_answer"] = True
    return redirect(url_for("revision_carte"))

@app.route("/revision/suivante/<int:idcarte>/<int:savais>", methods=["POST"])
@f.statuts_obligatoires()
def carte_suivante(idcarte, savais):
    idutilisateur = session.get("idutilisateur")
    revision_actuelle = bdd.get_revision(idutilisateur, idcarte)

    if savais == 1:
        idboite = revision_actuelle["idboite"] if revision_actuelle else bdd.get_idboite_by_rang(1)["idboite"]
        rang_actuel = bdd.get_rang_by_idboite(idboite)["rang"]
        nouveau_rang = min(rang_actuel + 1, 5)
    else:
        nouveau_rang = 1

    nouveau_idboite = bdd.get_idboite_by_rang(nouveau_rang)["idboite"]

    if revision_actuelle:
        bdd.update_revision(idutilisateur, idcarte, nouveau_idboite)
    else:
        bdd.add_revision(idutilisateur, idcarte, nouveau_idboite)

    session["revision_index"] += 1
    session["show_answer"] = False
    return redirect(url_for("revision_carte"))