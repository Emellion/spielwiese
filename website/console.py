from flask import Blueprint
from flask import render_template, request, flash, redirect, url_for
from website.models import Admin
from website import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user



def login():
    admin_login_name = ""
    admin_login_passwort = ""
    while admin_login_name == "":
        admin_login_name = input("Bitte gib deinen login-namen ein: ")

    while admin_login_passwort == "":
        admin_login_passwort = input("Bitte gib dein Admin-Passwort ein: ")

    admin_name = Admin.query.filter_by(name=admin_login_name).first()
    if admin_name:
        if check_password_hash(admin.password, admin_login_passwort):
            login_user()
            print("Erfolgreich angemeldet.")

login()



userInput = "null"

# while userInput:
#     userInput = input(">")
#     if userInput == login:
#         login()

