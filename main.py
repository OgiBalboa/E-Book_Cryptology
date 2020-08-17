"""
Bu uygulama Marmara Üniversitesi Teknoloji Fakültesi Mekatronik Mühendisliği
Bölümü için geliştirilmiştir. E-book kitapları için şifreleme sistemidir.
E-book okuyucu uygulama Lector ' a teşekkürlerimizle.

@yazar: ogibalboa
Tarih : 05.06.2020
"""
from PyQt5 import QtCore, QtGui, QtWidgets,uic
from auth import Ui_MainWindow
from subprocess import call
from db import db,permission
import os
import firebase
from pylocker import ServerLocker
from cryptography.fernet import Fernet
if permission() == False:
    exit()
#lock = ServerLocker(password =
db = db()
class MainMenu(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainMenu,self).__init__()
        uic.loadUi('mainmenu.ui',self)
        #self.setupUi(window)
        self.submit_button.clicked.connect(self.submit)
        self.register_button.clicked.connect(self.register_page)
        self.register_frame.setHidden(True)
        self.reg_submit_button.clicked.connect(self.register)
        self.reg_cancel_button.clicked.connect(self.back)
        self.add_book_btn.clicked.connect(lambda: self.add_book(self.code_input.text()))
    def back(self):
        self.register_frame.setHidden(True)
        self.signIn_frame.setHidden(False)
    def register_page(self):
        self.register_frame.setVisible(True)
        self.signIn_frame.setHidden(True)
    def check_inputs(self,hint = None):
        if self.pass_input.text() == "":
            return True
        if hint == "signin" and len(self.password_input.text()) > 5 :
            return True
        elif hint == "register" and len(self.reg_password_input.text()) > 5:
            self.admin_key = db.download_key()[0]
            if self.register_key.text() == self.admin_key:
                return True
            else:
                return False
        else :
            return False
    def submit(self):
        if self.check_inputs(hint=  "signin") == False:
            return False
        elif self.pass_input.text() == "":
            email ="170216009@gmail.com"
            password = "gfb.1907"
        else:
            email = self.username_input.text() + "@gmail.com"
            self.password_input.text()
        if db.sign(email =email ,password =password) == None:
            self.auth_frame.hide()
            #os.system("python ./lector/__main__.py")
    def register(self):
        if self.check_inputs(hint=  "register") == False:
            print("olmadi")

            return False
        email = self.reg_username_input.text() + "@gmail.com"
        print(db.register(email = email ,password=self.reg_password_input.text()))
    def add_book(self,code):
        self.code = code
        print(db.auth.current_user)
        db.database.child("/books/tasit_mekatronik").set(
                {"code":code},token=db.user['localId']
                )
        print(db.database.child("/books/tasit_mekatronik").get())
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("fusion")
    menu = MainMenu()
    #ui = Auth(mainwin)
    menu.show()
    sys.exit(app.exec_())
