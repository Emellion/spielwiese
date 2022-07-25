from flask import Blueprint
from flask import render_template, request, flash, redirect, url_for
from .models import Customer, Admin
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
import logging




views = Blueprint("views", __name__)


@views.route("/", methods=["GET", "POST"])
def auth():
    if request.method == "POST":
        admin_login_name = request.form.get("admin_name")
        admin_login_password = request.form.get("admin_password")
        admin = Admin.query.filter_by(name=admin_login_name).first()
        if admin:
            if check_password_hash(admin.password, admin_login_password):
                login_user(admin, remember=True)
                return redirect("/alle_kunden")
            else:
                flash("Passwort stimmt nicht überein.", category="error")
        else:
            flash("Es existiert kein Nutzer mit diesem namen. ", category="error")

    return render_template("auth.html", admin=current_user)

@views.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Erfolgreich Abgemeldet.", category="success")
    return redirect(url_for("views.auth"))


@views.route("/mitglied_auth", methods=["GET","POST"])
def mitglied_auth():
    return render_template("mitglied_auth.html")


@views.route("/alle_kunden", methods=["GET", "POST"])
@login_required
def alle_kunden():
    if request.method == "POST" and request.form["del"]:
        kunde_id = request.form.get("del")
        db.engine.execute(f"DELETE FROM customer WHERE id = {kunde_id}")
        db.session.commit()
        flash("Kunde entfernt.", category="success")
        return redirect(url_for("views.alle_kunden"))
    else:
        return render_template("alle_kunden.html", admin=current_user)


@views.route("/kunde_bearbeiten", methods=["GET", "POST"])
@login_required
def kunde_bearbeiten():
    if request.method == 'POST' and request.form.get("edit"):
        kunde_id = request.form["edit"]
        kunde = Customer.query.filter_by(id=kunde_id).first()
        return render_template("kunde_bearbeiten.html", admin=current_user,
                                                        kunde_firstName=kunde.firstName,
                                                        kunde_lastName=kunde.lastName,
                                                        kunde_id=kunde.id,
                                                        kunde_email = kunde.email,
                                                        kunde_birthDate = kunde.birthDate)

    elif request.method == 'POST' and request.form.get("save"):
        kunde_id = request.form["save"]
        kunde = Customer.query.filter_by(id=kunde_id).first()
        kunde_email_new = request.form["email"]
        kunde_firstName_new = request.form["firstName"]
        kunde_lastName_new = request.form["lastName"]
        kunde_birthDate_new = request.form["birthDate"]

        logging.basicConfig()
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
        db.engine.execute("""UPDATE customer SET  
                                            email = :email, 
                                            firstName = :firstName, 
                                            lastName = :lastName, 
                                            birthDate = :birthDate 
                                            WHERE id = :id""", {

                                            "email": kunde_email_new,
                                            "firstName": kunde_firstName_new,
                                            "lastName": kunde_lastName_new,
                                            "birthDate": kunde_birthDate_new,
                                            "id": kunde_id
                                            })
        db.session.commit()
        return redirect(url_for("views.alle_kunden"))

    return render_template("kunde_bearbeiten.html")


@views.route("/search", methods=["GET", "POST"])
@login_required
def search():
    char = "@"
    if request.method == 'POST' and request.form["searchbar"]:
        global keyword
        keyword = request.form.get("searchbar")
        global results
        if keyword.isalpha() and char not in keyword:
            results = db.engine.execute(f"""
                                SELECT * FROM customer WHERE firstName LIKE '%{keyword}%' OR lastName LIKE '%{keyword}%'
                                """)

        elif char in keyword:
            results = db.engine.execute(f"""
                                SELECT * FROM customer WHERE email LIKE '%{keyword}%'
                                """)

        elif keyword.isnumeric():
            results = db.engine.execute(f"""
                                SELECT * FROM customer WHERE id LIKE '{keyword}'
                                """)

        elif keyword == "":
            return redirect(url_for("views.alle_kunden"))

    return render_template("alle_kunden_search.html", admin=current_user, results=results)




@views.route("/anlegen", methods=["GET", "POST"])
@login_required
def kunde_anlegen():
    if request.method == "POST":
        email = request.form.get("email")
        firstName = request.form.get("firstName")
        lastName = request.form.get("lastName")
        birthDate = request.form.get("birthDate")


        if len(firstName) < 2:
            flash("Der Vorname muss mindestens zwei Buchstaben haben.", category="error")
        elif firstName[0].isalpha() == False:
            flash("Der erste Charakter eines Vornamens muss ein Buchstabe sein", category="error")
        elif lastName[0].isalpha() == False:
            flash("Der erste Charakter eines Nachnamens muss ein Buchstabe sein", category="error")
        elif lastName == "":
            flash("Bitte gib den Nachnamen des Kunden ein.", category="error")
        elif birthDate == "":
            flash("Bitte gib das Geburtsdatum an.")
        else:
            neuer_kunde = Customer(email=email, firstName=firstName, lastName=lastName, birthDate=birthDate, admin_id=current_user.id)
            db.session.add(neuer_kunde)
            db.session.commit()
            flash("Kunde erstellt!", category="success")

    return render_template("kunde_anlegen.html")


@views.route("/admin_anlegen", methods=["POST", "GET"])
def admin_anlegen():
    if request.method == "POST":
        admin_name = request.form["admin1_name"]
        admin_email = request.form["admin1_email"]
        password = request.form["admin1_password"]
        password_confirm = request.form["admin1_password_confirm"]
        admin_email_candidate = Admin.query.filter_by(email=admin_email).first()
        if admin_email_candidate:
            flash("Diese E-Mail existiert bereits.", category="error")
        elif password != password_confirm:
            flash("Die Passwörter stimmen nicht überein.", category="error")
        elif admin_name == "":
            flash("Bitte geben Sie einen Namen ein.", category="error")
        elif admin_email == "":
            flash("Bitte geben Sie eine E-Mail ein.", category="error")
        elif password == "":
            flash("Bitte geben Sie ein Passwort ein.", category="error")
        elif len(password) < 4:
            flash("Passwort ist zu kurz.", category="error")
        else:
            neuer_admin = Admin(name=admin_name, email=admin_email, password=generate_password_hash(password, method="sha256"))
            db.session.add(neuer_admin)
            db.session.commit()

            admin = Admin.query.filter_by(name=admin_name).first()
            if admin:
                if check_password_hash(admin.password, password):
                    flash("Erfolgreich angemeldet.", category="success")
                    login_user(admin, remember=True)
                    return redirect(url_for("views.alle_kunden"))
            return redirect(url_for("views.alle_kunden"))

    return render_template("create_admin.html")


@views.route("/delete_customer", methods=['POST', 'GET'])
@login_required
def delete_user():
    if request.method == "POST":
        kunde_id = request.form["delete"]
        kunde = Customer.query.filter_by(id=kunde_id).first()
        db.engine.execute(f"DELETE FROM customer WHERE id ={kunde_id}")
        db.session.commit()
        flash("Kunde entfernt.", category="success")
        return render_template("/alle_kunden")


@views.route("/alle_löschen", methods=['POST', 'GET'])
@login_required
def alle_löschen():
    admin_id = current_user.get_id()
    if request.method == 'POST' and request.form.get("delete_all_no"):
        return redirect(url_for("views.alle_kunden"))
    elif request.method == 'POST' and request.form.get("delete_all_yes"):
        db.engine.execute(f"DELETE FROM customer WHERE admin_id = {admin_id};")
        db.session.commit()

        return redirect(url_for("views.alle_kunden"))
    return render_template("alle_löschen.html", admin=current_user)




