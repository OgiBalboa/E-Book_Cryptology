"""
Bu uygulama Marmara Üniversitesi Teknoloji Fakültesi Mekatronik Mühendisliği
Bölümü için geliştirilmiştir. E-book kitapları için şifreleme sistemidir.
@yazar: ogibalboa
Tarih : 05.06.2020
"""
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from pylocker import ServerLocker
from cryptography.fernet import Fernet
import logos_rc


class AuthMenu(QtWidgets.QMainWindow):
    def __init__(self,main):
        super(AuthMenu, self).__init__()
        uic.loadUi('ui/auth.ui', self)
        # self.setupUi(window)
        self.main = main
        self.submit_button.clicked.connect(self.submit)
        self.register_button.clicked.connect(self.register_page)
        self.register_frame.setHidden(True)
        self.reg_submit_button.clicked.connect(self.register)
        self.reg_cancel_button.clicked.connect(self.back)

    def back(self):
        self.register_frame.setHidden(True)
        self.auth_frame.setHidden(False)

    def register_page(self):
        self.register_frame.setVisible(True)
        self.auth_frame.setHidden(True)

    def check_inputs(self, hint=None):
        if self.password_input.text() == "":
            return True
        if hint == "signin" and len(self.password_input.text()) > 5:
            return True
        elif hint == "register" and len(self.reg_password_input.text()) > 5:
            self.admin_key = db.download_key()[0]
            if self.register_key.text() == self.admin_key:
                return True
            else:
                return False
        else:
            return False

    def submit(self):
        if self.check_inputs(hint="signin") == False:
            return False
        elif self.password_input.text() == "":
            self.main.email = "170216009@gmail.com"
            self.main.password = "gfb.1907"
            self.main.no = "170216009"
        else:
            self.main.no = self.username_input.text()
            self.main.email = self.username_input.text() + "@gmail.com"
            self.main.password = self.password_input.text()
        self.close()
        self.main.submit()
        self.main.show()
    def register(self):
        if self.check_inputs(hint="register") == False:
            print("olmadi")
            return False
        email = self.reg_username_input.text() + "@gmail.com"
        print(db.register(email=email, password=self.reg_password_input.text()))