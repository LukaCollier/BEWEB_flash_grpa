from flask import flash, redirect, session
from functools import wraps
#Vérifie que l'utilisateur est connecté et possède un rôle autorisé
def statuts_obligatoires(*statuts_autorises):
    def decorateur(f):
        @wraps(f)
        def wrapper(*args,**kwargs):
            #Vérifie que l'utilisateur est connecté
            if 'idUser' not in session or 'statut' not in session:
                flash("Vous devez être connecté pour accéder à cette page.", "danger")
                return redirect("/signin")
            if not statuts_autorises:
                return f(*args, **kwargs)
            #Vérifie que le rôle est autorisé 
            if session['statut'] not in statuts_autorises:
                flash("Vous n'avez pas les droits pour accéder à cette page.", "danger")
                #Redirection selon rôle
                routes = {
                    "administrateur":"/admin",
                    "gestionnaire":"/gestion",
                    "pilote":"/gestion"
                }
                route_suivante = routes.get(session['statut'],"/")
                return redirect(route_suivante)
            return f(*args,**kwargs)
        return wrapper
    return decorateur