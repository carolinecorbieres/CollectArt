from werkzeug.security import generate_password_hash, check_password_hash
# importation de generate_password_hash et check_password_hash depuis werkzeug pour hascher les mots de passe
from flask_login import UserMixin
# importation d'UserMixin qui implémente par défaut les méthodes is_authenticated, is_active, is_anonymous, get_id(identifier)

from .. app import db, login
# importation de la BDD et de login pour gérer les utilisateur·rice·s

class User(UserMixin, db.Model):
    __tablename__ = "user"
    user_id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    user_name = db.Column(db.Text, nullable=False)
    user_login = db.Column(db.String(45), nullable=False)
    user_email = db.Column(db.Text, nullable=False)
    user_password = db.Column(db.String(100), nullable=False)
    author_collection = db.relationship("Authorship_collection", back_populates="user_collection")
    author_work = db.relationship("Authorship_work", back_populates="user_work")

    def get_id(self):
        """
        Retourne l'id de l'objet actuellement utilisé
        :return: ID de l'utilisateur·rice
        :rtype: int
        """
        return(self.user_id) 

    @staticmethod
    # @staticmethod permet d'appeler la fonction de la manière suivante : user = User.identification(login, password)
    def identification(login, password):
        """ 
        Identifie un utilisateur·rice. Si cela fonctionne, renvoie les données de l'utilisateur·rice.
        :param login: Login de l'utilisateur·rice
        :param password: Mot de passe envoyé par l'utilisateur·rice
        :return: Si réussite, données de l'utilisateur·rice. Sinon None
        :rtype: User or None
        """
        user = User.query.filter(User.user_login == login).first()
        if user and check_password_hash(user.user_password, password):
            return user
        # si le login et le mot de passe correspondent, on renvoie la variable user
        return None

    @staticmethod
    def creer(login, email, name, password):
        """ 
        Crée un compte utilisateur·rice. Retourne un tuple (booléen, User ou liste). Si il y a une erreur, la fonction 
        renvoie False suivi d'une liste d'erreurs. Sinon, elle renvoie True suivi de la donnée enregistrée
        :param login: Login de l'utilisateur·rice
        :param email: Email de l'utilisateur·rice
        :param name: Nom de l'utilisateur·rice
        :param password: Mot de passe de l'utilisateur·rice (Minimum 6 caractères)
        :return: tuple
        """
        errors = []
        # création d'une liste vide pour y stocker les erreurs
        if not login:
            errors.append("le login fourni est vide")
        if not email:
            errors.append("l'email fourni est vide")
        if not name:
            errors.append("le nom fourni est vide")
        if not password or len(password) < 6:
            errors.append("le mot de passe fourni est vide ou trop court")
        # conditions pour vérifier que les champs du formulaire sont complétés

        uniques = User.query.filter(db.or_
            (User.user_email == email, User.user_login == login)
        ).count()
        if uniques > 0:
            errors.append("l'email ou le login sont déjà utilisés")
        # on vérifie que personne n'a utilisé cet email ou ce login

        if len(errors) > 0:
            return False, errors
        # Si on a au moins une erreur

        user = User(
            user_name=name,
            user_login=login,
            user_email=email,
            user_password=generate_password_hash(password)
        )
        # On crée un utilisateur·rice

        try:
            db.session.add(user)
            # On ajoute l'utilisateur·rice à la BDD
            db.session.commit()
            # On envoie le paquet

            return True, user
            # On renvoie l'utilisateur·rice

        except Exception as error:
            return False, [str(error)]

    @staticmethod
    @login.user_loader
    def trouver_utilisateur_via_id(user_id):
        """
        Permet de récupérer un·e utilisateur·rice en fonction de son identifiant
        :return: ID de l'utilisateur·rice
        :rtype: int
        """
        return User.query.get(int(user_id))
