from PyQt5 import QtWidgets, uic
import json
from GuiClasses.Main_window import MainWindow
from GuiClasses.Forgot_password_window import ForgotWindow
from GuiClasses.Register_window import RegisterWindow
from SidePackage.Error import pop_alert
import time
import requests


class LoginWindow(QtWidgets.QMainWindow):
    def __init__(self, URLs):
        super(LoginWindow, self).__init__()
        uic.loadUi('UiFiles/Login_window.ui', self)
        self.URLs = URLs

        self.initUi()

        self.show()

    def initUi(self):
        self.button_login = self.findChild(QtWidgets.QPushButton, 'button_login')
        self.button_forgot = self.findChild(QtWidgets.QPushButton, 'button_forgot')
        self.button_register = self.findChild(QtWidgets.QPushButton, 'button_register')
        self.lineEdit_username = self.findChild(QtWidgets.QLineEdit, 'lineEdit_username')
        self.lineEdit_password = self.findChild(QtWidgets.QLineEdit, 'lineEdit_password')
        self.checkBox_remember = self.findChild(QtWidgets.QCheckBox, 'checkBox_remember')
        self.opened_main_window = False
        self.button_login.pressed.connect(self.login_button_pressed)
        self.button_forgot.pressed.connect(self.forgot_button_pressed)
        self.button_register.pressed.connect(self.register_button_pressed)

        self.load_users_credentials()

    def login_button_pressed(self):
        username = self.lineEdit_username.text()
        password = self.lineEdit_password.text()

        # Validate input data
        if not self.validate_data(username, password):
            self.lineEdit_username.setPlaceholderText("Podaj najpierw login i hasło!")
            return

        # remember user login data
        if self.checkBox_remember.isChecked():
            self.save_users_credentials(username, password)
        else:
            self.delete_users_credentials()

        # try for present server
        try:
            url = self.URLs[0] + '/chat/api-token-auth/'
            payload = {'username': username, 'password': password}
            r = requests.post(url, data=payload)
            if r.status_code == 200:
                self.close()
                data = r.json()
                token = data["token"]
                user_id = data["user_id"]
                if not self.opened_main_window:
                    self.open_main_window(token, user_id)
                self.opened_main_window = True

            else:
                pop_alert("Niepoprawne dane logowania!")
        except requests.ConnectionError:

            # Todo okienko z bledem sieci
            print("Błąd serwera")
            pop_alert("Błąd sieci, sprawdź połączenie.")

    def forgot_button_pressed(self):
        self.ui = ForgotWindow(self)
        self.setDisabled(True)

    def register_button_pressed(self):
        self.ui = RegisterWindow(self)
        self.setDisabled(True)

    def save_users_credentials(self, username, password):
        # Saves users credentials into json file
        with open("cred.entials", "w") as f:
            json.dump((username, password), f)
            f.close()

    def load_users_credentials(self):
        # Loads saved users credentials from file into lineEdits
        try:
            # Open file if exists
            with open("cred.entials", "r") as f:
                credentials = json.load(f)
                self.lineEdit_username.setText(credentials[0])
                self.lineEdit_password.setText(credentials[1])

                # If there was saved any data set checkBox saved
                if credentials[0] != "":
                    self.checkBox_remember.setChecked(True)
                f.close()

        # There is no such file
        except FileNotFoundError:
            pass
        # This File is empty
        except json.decoder.JSONDecodeError:
            pass

    def delete_users_credentials(self):
        # Empty the file with credentials
        open("cred.entials", "w").close()

    def open_main_window(self, token_id, user_id):
        # open new window
        self.ui = MainWindow(token_id, user_id, self.URLs, self)

    def validate_data(self, login, password):
        # Checks if login/password is not empty
        if login and password:
            return True
        else:
            return False
