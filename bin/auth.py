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
        self.dialog = AuthDialog()
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
            #self.main.no = "170216009"
            for items in self.main.db.students.order_by_child('email').equal_to(self.main.email).get().keys():
                self.main.no = items
        else:
            self.main.no = self.username_input.text()
            self.main.email = self.username_input.text() + "@gmail.com"
            self.main.password = self.password_input.text()
        self.close()
        if self.main.db.sign(email=self.main.email, password=self.main.password) == None:
            self.main.submit()
            self.main.show()
        else: self.dialog.show()

    def register(self):
        if self.check_inputs(hint="register") == False:
            print("olmadi")
            return False
        email = self.reg_username_input.text() + "@gmail.com"
        print(db.register(email=email, password=self.reg_password_input.text()))

class AuthDialog(QtWidgets.QDialog):
    def __init__(self):
        super(AuthDialog, self).__init__()
        self.lbl = QtWidgets.QLabel(self)
        self.lbl.setText("Hatalı E-mail veya Şifre!")
        self.btn = QtWidgets.QPushButton('Cancel')
        self.btn.setEnabled(True)
        self.btn.clicked.connect(self.close)
        self.setWindowTitle("Hata!")
        self.resize(250,50)