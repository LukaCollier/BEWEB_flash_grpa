# 📚 Documentation Complète - BEWEB Flashcards

## 📋 Table des Matières
1. [Vue d'ensemble du projet](#vue-densemble)
2. [Structure du projet](#structure)
3. [Configuration](#configuration)
4. [Backend - Views (Routes)](#backend--views)
5. [Backend - Modèle BDD](#backend--modèle-bdd)
6. [Backend - Générique BDD](#backend--générique-bdd)
7. [Backend - Controller/Functions](#backend--controllerfonctions)
8. [Frontend - Templates](#frontend--templates)
9. [Flux d'authentification](#flux-dauthentification)

---

## Vue d'ensemble

**BEWEB** est une application web Flask pour la gestion de **flashcards éducatives** avec un système d'authentification multi-rôles. Les utilisateurs peuvent créer des comptes, gérer des paquets de flashcards, et accéder à différentes fonctionnalités selon leur rôle.

### Rôles disponibles:
- 👤 **Utilisateur standard**: Accès aux flashcards
- 🔧 **Gestionnaire**: Gestion des paquets et flashcards
- 🛡️ **Administrateur**: Administration complète + gestion des utilisateurs

---

## Structure

```
BEWEB.github.io/
├── run.py                          # Point d'entrée de l'application
├── myApp/
│   ├── config.py                   # Configuration globale
│   ├── views.py                    # Toutes les routes Flask
│   ├── ienac_flashcards_groupea.sql    # Schéma BDD
│   ├── controller/
│   │   ├── function.py             # Décorateurs et utilitaires
│   │   └── hash.py                 # Outil de hachage SHA256
│   ├── model/
│   │   ├── bdd.py                  # Requêtes métier (métier)
│   │   └── bddGen.py               # Fonctions génériques BDD
│   ├── static/
│   │   ├── css/                    # Feuilles de styles
│   │   ├── fonts/                  # Polices
│   │   ├── images/                 # Images du site
│   │   └── js/                     # Scripts JavaScript
│   └── template/
│       ├── layout/
│       │   ├── header.html         # En-tête HTML
│       │   ├── nav.html            # Barre de navigation
│       │   ├── footer.html         # Pied de page
│       │   └── footermain.html     # Pied de page principal
│       ├── team/                   # Pages équipe
│       └── [pages HTML]            # Pages principales
```

---

## Configuration

**Fichier: `myApp/config.py`**

```python
ENV = "development"
DEBUG = True                    # Mode debug activé
SEND_FILE_MAX_AGE_DEFAULT = 0  # Pas de cache des fichiers statiques
SECRET_KEY = "pouletteetpoulet" # Clé secrète Flask (⚠️ À changer en prod!)

WEB_SERVER = {
    "host": "localhost",
    "port": 8080,
}

DB_SERVER = {
    "user": "root",
    "password": "",
    "host": "localhost",
    "port": 3306,
    "database": "ienac25_flashcards_groupea",
    "raise_on_warnings": True
}
```

### Point d'entrée: `run.py`
Lance l'application Flask sur http://localhost:8080 en mode debug.

---

## Backend - Views

**Fichier: `myApp/views.py`**

### 🔓 Routes Publiques

#### `GET / · index()`
- **Description**: Page d'accueil
- **Template**: `index.html`

#### `GET /about · about()`
- **Description**: Page "À propos"
- **Template**: `about.html`

#### `GET /contact · contact()`
- **Description**: Page de contact
- **Template**: `contact.html`

#### `GET /team/<member> · team_member()`
- **Description**: Pages des membres de l'équipe
- **Templates**: `team/camille.html`, `team/etienne.html`, `team/luka.html`, `team/darya.html`

---

### 🔐 Routes d'Authentification

#### `GET/POST /signin · signin()`
- **Description**: Page de connexion
- **Template**: `signin.html`
- **Méthode POST**: Gérée par `/connecter`

#### `POST /connecter · connect()`
- **Description**: Traite la connexion utilisateur
- **Paramètres POST**: `login` (pseudo/email), `mdp` (mot de passe)
- **Processus**:
  1. Vérifie les identifiants avec `bdd.verifAuthData()`
  2. Remplit la session avec les données utilisateur
  3. Redirige selon le rôle:
     - Administrateur → `/admin`
     - Gestionnaire → `/gestion`
     - Utilisateur → `/banques`
- **Errors**: "Identifiants incorrects" si login/mdp invalides

#### `GET /logout · logout()`
- **Description**: Déconnexion
- **Action**: Efface la session et redirige à `/signin`

#### `GET/POST /signup · signup()`
- **Description**: Page d'inscription
- **Template**: `signup.html`
- **Champs formulaire**:
  - `firstname`: Prénom (optionnel)
  - `lastname`: Nom (optionnel)
  - `email`: Email (obligatoire, unique)
  - `statut`: Rôle (obligatoire)
  - `pseudo`: Pseudonyme (obligatoire, unique)
- **Processus**:
  1. Vérifie que l'email n'existe pas
  2. Vérifie que le pseudo n'existe pas
  3. Génère un mot de passe temporaire (5 caractères)
  4. Hache le mot de passe en SHA256
  5. Insère l'utilisateur en BDD
  6. **NOUVEAU**: Remplit la session avec les données utilisateur
  7. Redirige à `/modifMdp`
- **Validation**: Email et pseudo uniques

#### `GET/POST /modifMdp · modifMdp()`
- **Description**: Modification du mot de passe
- **Template**: `modifMdp.html`
- **Accès**: Connecté obligatoire
- **Champs**:
  - `ancienmdp`: Ancien mot de passe
  - `nvmdp`: Nouveau mot de passe (min. 8 caractères)
  - `confirmmdp`: Confirmation nouveau mot de passe
- **Validations**:
  - L'ancien mot de passe doit correspondre
  - Nouveau mot de passe et confirmation doivent matcher
  - Minimum 8 caractères
- **Après succès**: Redirige à `/signin`

---

### 🔒 Routes Privées

#### `GET /banques · banques()`
- **Description**: Liste des banques de flashcards
- **Template**: `banques.html`
- **Accès**: Connecté obligatoire (tous les rôles)
- **Décorateur**: `@f.statuts_obligatoires()`
- **Données**: Récupère les catégories et compte les cartes

#### `GET /banques/<int:bank_id> · banque_detail(bank_id)`
- **Description**: Détail d'une banque avec les flashcards
- **Template**: `banques.html`
- **Accès**: Connecté obligatoire
- **Paramètres**: ID de la catégorie
- **Données**: Liste des cartes de la banque

#### `GET /admin · admin()`
- **Description**: Page d'administration
- **Template**: `admin.html`
- **Accès**: Administrateur uniquement
- **Décorateur**: `@f.statuts_obligatoires('administrateur')`
- **Données**: Liste complète des utilisateurs

#### `GET /delete_user/<idutilisateur> · delete_user(idutilisateur)`
- **Description**: Supprime un utilisateur
- **Accès**: Administrateur uniquement
- **Paramètres**: ID de l'utilisateur à supprimer
- **Action**: Appelle `bdd.delete_userData()`
- **Redirection**: Retour à `/admin`

#### `GET /gestion · gestion()`
- **Description**: Page de gestion
- **Template**: `gestion.html`
- **Accès**: Gestionnaire ou Administrateur
- **Décorateur**: `@f.statuts_obligatoires('gestionnaire', 'administrateur')`

#### `GET /paquet · paquet()`
- **Description**: Gestion des paquets
- **Template**: `paquet.html`
- **Accès**: Connecté obligatoire

#### `GET /updatecarte · updatecarte()`
- **Description**: Création/mise à jour de cartes
- **Template**: `creationcartes.html`
- **Accès**: Connecté obligatoire

---

## Backend - Modèle BDD

**Fichier: `myApp/model/bdd.py`**

### Fonctions de Requête

#### `get_membresData()`
```python
Retourne: List[Dict] - Liste de tous les utilisateurs
Colonnes: idutilisateur, pseudo, mail, nom, prenom, statut
```

#### `check_pseudo(pseudo: str)`
```python
Vérifie si un pseudo existe déjà
Paramètre: pseudo (str)
Retourne: Dict ou None
Utilisation: Validation lors de l'inscription
```

#### `check_email(email: str)`
```python
Vérifie si un email existe déjà
Paramètre: email (str)
Retourne: Dict ou None
Utilisation: Validation lors de l'inscription
```

#### `verifLogin(login: str)`
```python
Cherche un utilisateur par pseudo OU email
Paramètre: login (str) - pseudo ou email
Retourne: Dict ou None
```

#### `getMdp(idutilisateur: int)`
```python
Récupère le mot de passe hashé d'un utilisateur
Paramètre: idutilisateur (int)
Retourne: str - Hash SHA256 du mot de passe
```

#### `add_userData(rform: Dict, mdp_hash: str, msg: Dict)`
```python
Insère un nouvel utilisateur en BDD
Paramètres:
  - rform: Dictionnaire du formulaire
    {pseudo, email, lastname, firstname, statut}
  - mdp_hash: Mot de passe hashé SHA256
  - msg: Dictionnaire de messages {ok, echec}
Retourne: int - ID du nouvel utilisateur
```

#### `update_userMdpData(newMdp: str, iduser: int)`
```python
Met à jour le mot de passe d'un utilisateur
Paramètres:
  - newMdp: Nouveau mot de passe hashé
  - iduser: ID de l'utilisateur
Retourne: bool
```

#### `verifAuthData(login: str, mdp: str)`
```python
Vérifie les identifiants de connexion
Paramètres:
  - login: Pseudo ou email
  - mdp: Mot de passe en clair
Retourne: Dict (données utilisateur) ou None
Processus:
  1. Cherche l'utilisateur par pseudo/email
  2. Hache le mot de passe fourni
  3. Compare avec le hash stocké
  4. Supporte les anciens mots de passe non hashés
```

#### `get_userById(idutilisateur: int)` ✨ **NOUVEAU**
```python
Récupère les données complètes d'un utilisateur par ID
Paramètre: idutilisateur (int)
Retourne: Dict
Colonnes: idutilisateur, pseudo, mail, nom, prenom, statut
Utilisation: Remplissage de la session après inscription
```

#### `delete_userData(idutilisateur: int, msg: Dict)`
```python
Supprime un utilisateur de la BDD
Paramètres:
  - idutilisateur: ID à supprimer
  - msg: Dictionnaire de messages {ok, echec}
Retourne: bool
```

---

## Backend - Générique BDD

**Fichier: `myApp/model/bddGen.py`**

Fournit les fonctions bas-niveau pour communiquer avec MySQL.

### Gestion de la Connexion

#### `connexion()`
```python
Crée une connexion depuis le pool MySQL
Retourne: MySQLConnection ou None
- Utilise un pool de 10 connexions
- Gère les erreurs et affiche les messages
```

### Requêtes Génériques

#### `queryData(type: str, sql: str, param: Tuple, funct_name: str, message: Dict)`
```python
Fonction centrale pour toutes les requêtes
Paramètres:
  - type: 'select', 'selectOne', 'add', 'addMany', 'update', 'delete'
  - sql: Requête SQL avec placeholders %s
  - param: Tuple des paramètres
  - funct_name: Nom de la fonction appelante (pour logs)
  - message: Dict optionnel {ok, echec} pour messages flash

Types de retour selon 'type':
  - 'select': List[Dict] - Tous les résultats
  - 'selectOne': Dict ou None - Un seul résultat
  - 'add'/'addMany': int - ID inséré (lastrowid)
  - 'update'/'delete': bool - True si succès
  
Gère:
  - Connexion et pool MySQL
  - Transactions (commit après chaque requête)
  - Messages flash (succès/erreur)
  - Logs colorisés en terminal
```

### Fonctions Simplifiées

#### `selectOneData(funct_name: str, sql: str, param: Tuple, message: Dict)`
```python
Wrapper pour requête SELECT retournant 1 résultat
Retourne: Dict ou None
```

#### `selectData(funct_name: str, sql: str, param: Tuple, message: Dict)`
```python
Wrapper pour requête SELECT retournant plusieurs résultats
Retourne: List[Dict]
```

#### `addData(funct_name: str, sql: str, param: Tuple, message: Dict)`
```python
Wrapper pour INSERT
Retourne: int - ID du nouvel enregistrement
```

#### `updateData(funct_name: str, sql: str, param: Tuple, message: Dict)`
```python
Wrapper pour UPDATE
Retourne: bool
```

#### `deleteData(funct_name: str, sql: str, param: Tuple, message: Dict)`
```python
Wrapper pour DELETE
Retourne: bool
```

---

## Backend - Controller/Fonctions

**Fichier: `myApp/controller/function.py`**

### Décorateur d'Authentification

#### `@statuts_obligatoires(*statuts_autorises)`
```python
Décorateur pour protéger les routes
Paramètres: Statuts autorisés ('gestionnaire', 'administrateur', etc.)

Comportement:
  1. Vérifie que l'utilisateur est connecté
     - Si non: flash "Vous devez être connecté" → redirect /signin
  
  2. Vérifie que le statut est autorisé
     - Si non autorisé: flash "Pas de droits" → redirect selon rôle
     - Administrateur → /admin
     - Gestionnaire → /gestion
     - Autre → /
  
  3. Si tout OK: exécute la route normalement

Utilisation:
  @app.route('/admin')
  @statuts_obligatoires('administrateur')
  def admin():
      # Code protégé
```

**Fichier: `myApp/controller/hash.py`**

Script utilitaire pour générer des hash SHA256:
```python
import hashlib
mdp = 'admin'
mdp_hash = hashlib.sha256(mdp.encode()).hexdigest()
print(mdp_hash)
```

---

## Frontend - Templates

**Dossier: `myApp/template/`**

### Layout (Composants réutilisables)

#### `layout/header.html`
- Déclaration HTML, tags meta, CSS
- Inclus sur toutes les pages

#### `layout/nav.html`
- Barre de navigation responsive
- Affiche: `{{ session.get('prenom') }} {{ session.get('nom') }}`
- Liens dynamiques selon le rôle
- Boutons Connexion/Déconnexion

#### `layout/footer.html`
- Pied de page réutilisable

#### `layout/footermain.html`
- Pied de page alternatif

### Pages Publiques

| Page | Fichier | Description |
|------|---------|-------------|
| Accueil | `index.html` | Page d'accueil |
| À propos | `about.html` | Informations sur le projet |
| Contact | `contact.html` | Page de contact |
| Équipe | `team/camille.html`, etc. | Présentation des membres |

### Pages d'Authentification

#### `signin.html`
- Formulaire de connexion
- Champs: login (pseudo/email), mdp
- Lien vers inscription

#### `signup.html`
- Formulaire d'inscription
- Champs: firstname, lastname, email, statut, pseudo
- Validation des champs obligatoires
- Messages d'erreur

#### `modifMdp.html`
- Formulaire de modification de mot de passe
- Champs: ancienmdp, nvmdp, confirmmdp
- Validations affichées

### Pages Privées

| Page | Fichier | Rôle |
|------|---------|------|
| Banques | `banques.html` | Tous |
| Paquets | `paquet.html` | Tous |
| Création de cartes | `creationcartes.html` | Tous |
| Gestion | `gestion.html` | Gestionnaire/Admin |
| Administration | `admin.html` | Admin |

---

## Flux d'Authentification

### 1️⃣ Inscription (Signup)

```
POST /signup
    ↓
Validation email/pseudo (uniques)
    ↓
Génération mot de passe temporaire
    ↓
SHA256 du mot de passe
    ↓
INSERT en BDD → get ID
    ↓
Récupération des données user (NOUVEAU)
    ↓
Remplissage de la session:
  - idUser
  - nom, prenom, mail, pseudo, statut
    ↓
Flash: "Mot de passe actuel: [mdp]"
    ↓
Redirect → /modifMdp
```

### 2️⃣ Modification Mot de Passe (modifMdp)

```
GET /modifMdp
    ↓
Affiche formulaire
    
POST /modifMdp
    ↓
Récupération de idUser depuis session
    ↓
Validation ancien mot de passe
    ↓
Vérification nouveaux mots de passe identiques
    ↓
Vérification longueur ≥ 8 caractères
    ↓
SHA256 du nouveau mot de passe
    ↓
UPDATE en BDD
    ↓
Flash: "Mot de passe modifié"
    ↓
Redirect → /signin
```

### 3️⃣ Connexion (Signin/Connect)

```
POST /connecter
    ↓
Récupération login et mdp
    ↓
Appel bdd.verifAuthData(login, mdp)
    ↓
Vérification identifiants
    ↓
Si erreur: Flash + Redirect /signin
    ↓
Si OK: Remplissage complet de la session
    ↓
Redirection selon rôle:
  - Admin → /admin
  - Gestionnaire → /gestion
  - User → /banques
```

### 4️⃣ Accès aux Pages Protégées

```
GET /route-protegee
    ↓
Vérification du décorateur @statuts_obligatoires(...)
    ↓
Vérifier 'idUser' en session
    ↓
Si non connecté: Flash + Redirect /signin
    ↓
Vérifier statut autorisé
    ↓
Si non autorisé: Flash + Redirect selon rôle
    ↓
Si OK: Exécution de la route
```

---

## 🔐 Sécurité

- ✅ **Hachage des mots de passe**: SHA256
- ✅ **Uniques**: Email et pseudo
- ✅ **Authentification**: Basée sur session Flask
- ✅ **Autorisation**: Décorateur par rôle
- ⚠️ **À améliorer**: 
  - Changement de clé secrète en production
  - HTTPS en production
  - Validation côté serveur renforcée
  - Protection CSRF
  - Rate limiting

---

## 📊 Structure de la Session

```python
session = {
    "idUser": int,           # ID de l'utilisateur
    "idutilisateur": int,    # Doublé (compatible avec ancien code)
    "nom": str,              # Nom de l'utilisateur
    "prenom": str,           # Prénom de l'utilisateur
    "mail": str,             # Email
    "pseudo": str,           # Pseudonyme
    "statut": str,           # 'administrateur' ou 'gestionnaire'
}
```

---

## 🚀 Démarrage de l'Application

```bash
python run.py
```

L'application se lance sur: **http://localhost:8080**

---

**Dernière mise à jour**: Mai 2026  
**Version**: 1.0 avec correction du bug "None None" à l'inscription
