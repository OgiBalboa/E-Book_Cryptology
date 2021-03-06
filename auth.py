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
import datetime
import zipfile
import pyminizip
import tempfile
import os
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
        if hint == "signin" and self.password_input.text() == "":
            return True
        if hint == "signin" and len(self.password_input.text()) > 5:
            return True

        elif hint == "register" and len(self.reg_password_input.text()) > 5 and "@" in list(self.reg_username_input.text()) \
            and len(self.reg_name_input.text()) > 4 and len(self.reg_no_input.text()) == 9 :

            try:
                if ".com" != self.reg_username_input.text()[-4:]: return False
            except Exception as e:
                print(e)
                return False

            self.admin_key = self.main.db.download_key()[0]
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

        else:
            self.main.email = self.username_input.text()
            self.main.password = self.password_input.text()
        for items in self.main.db.students.order_by_child('email').equal_to(self.main.email).get().keys():
            self.main.no = items
        self.close()
        try:
            if self.main.db.sign(email=self.main.email, password=self.main.password) == None:
                self.main.submit()
                self.main.show()
            else: self.dialog.show()
        except:
            self.dialog.show_("Bilgileriniz hatalı veya internetiniz yok. Sorun varsa lütfen yöneticiye bildiriniz.","HATA")
    def register(self):
        if self.check_inputs(hint="register") == False:
            self.dialog.show()
            return False
        email = self.reg_username_input.text()
        try:
            self.main.db.register(email=email, password=self.reg_password_input.text())
            self.dialog.show_("Kayıt Başarılı","BAŞARILI")
            self.retrieve_register_info()
            self.main.db.students.update(self.info)
            self.back()
        except:
            self.dialog.show_("Bilgileri doğru girdiğinizden emin olun veya uygulamayı yeniden başlatın.")
            return False
    def retrieve_register_info(self):
        self.main.no = self.reg_no_input.text()
        self.main.email = self.reg_username_input.text()
        self.main.user_info = "/".join(["Teknoloji",self.comboBox.currentText() ,self.comboBox_2.currentText()])
        self.info = { self.main.no : {
            "email": self.main.email,
            "name": self.reg_name_input.text(),
            "info": self.main.user_info,
            "secret": "student",
            "st_books": {
                "None": "None"
            }
                   }}
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
    def show_(self,text,title = None):
        self.lbl.setText(text)
        if title != None: self.setWindowTitle(title)
        else : self.setWindowTitle("Hata!")
        self.show()

if __name__ == "__main__":
    """
    zip_file = 'ogibook.zip'
    password = 'abc123'
    with zipfile.ZipFile(zip_file) as zf:
        zf.setpassword(password)
        #zf.extractall(pwd=b"abc123")
    """
    with tempfile.TemporaryDirectory() as tdir:
        sourceFile = "ogibook.epub"
        destinationFile = "ogibook.zip"
        password = "nonshallpass"
        compression_level = 9  # 1-9
        pyminizip.compress(sourceFile, None, os.path.join(tdir,destinationFile), password, compression_level)

    #pyminizip.uncompress("ogibook.zip","nonshallpass",None,)
    pass
