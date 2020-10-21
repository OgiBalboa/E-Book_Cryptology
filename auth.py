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
import pyminizip
import tempfile
import zipfile
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
        self.checkBox.stateChanged.connect(self.rememberme)
        self.dialog = AuthDialog()
        if self.main.ofdb.rememberme:
            self.checkBox.setCheckState(True)
            self.username_input.setText(self.main.ofdb.user_info[0])
    def rememberme(self,val):
        self.main.ofdb.setRememberme(bool(val))
    def back(self):
        self.register_frame.setHidden(True)
        self.auth_frame.setHidden(False)

    def register_page(self):
        self.register_frame.setVisible(True)
        self.auth_frame.setHidden(True)

    def check_inputs(self, hint=None):

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
            self.main.setWaiting(True,"Kullanıcı adı veya şifre hatalı ")
            return False
        else:
            self.main.email = self.username_input.text()
            self.main.password = self.password_input.text()
        try:
            for items in self.main.db.students.order_by_child('email').equal_to(self.main.email).get().keys():
                self.main.no = items
                if len(self.main.no) < 9:
                    self.main.setWaiting(True,"Sisteme Kaydınız Bulunamadı ")
                    return
        except Exception as e:
            print(e)
            if self.main.ofdb.login(self.main.email,self.main.password):
                self.close()
                self.main.login_time = datetime.datetime.now()
                self.main.submit()
                self.main.show()
                return
            else:
                self.main.setWaiting(True,"Kullanıcı adı veya şifre hatalı (lütfen son giriş yaptığınız bilgiler ile giriniz veya internet bağlantısını kontrol edin.")
                return

        try:
            if self.main.db.sign(email=self.main.email, password=self.main.password) == None:
                self.close()
                self.main.login_time = datetime.datetime.now()
                self.main.submit()
                self.main.show()
            else: self.dialog.show()
        except Exception as e:
            print(e)
            self.dialog.show_("Bilgileriniz hatalı veya internetiniz yok. Sorun varsa lütfen yöneticiye bildiriniz.")
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
        except Exception as e:
            print(e)
            self.dialog.show_("Bilgileri doğru girdiğinizden emin olun veya uygulamayı yeniden başlatın.\n HATA MESAJI \n" + str(e))
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
        self.lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.btn = QtWidgets.QPushButton('Cancel')
        self.btn.setEnabled(True)
        self.btn.clicked.connect(self.close)
        self.setWindowTitle("Hata!")
        self.resize(700,250)
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
        sourceFile = ["/home/ogibalboa/Desktop/PROJECTS/EBOOK/E-Book_Cryptology/marun-bks.json","/home/ogibalboa/Desktop/PROJECTS/EBOOK/E-Book_Cryptology/config.json"]
        destinationFile = "ogibook.zip"
        password = "gAAAAABfizzjPLF0CYNvBom-CLWpKGh_CHUqW2dVBZDWyB_M330W4IxiVDNUZhMFbVVdgcGkIKOtxyBWu-eIDYVXsy9TZmnvJw"
        compression_level = 9
        pyminizip.compress_multiple(sourceFile,["/","/"], "/home/ogibalboa/Desktop/PROJECTS/EBOOK/E-Book_Cryptology/marun-bks.zip", password, compression_level)
    """
    pw = "pRmgMa8T0INjEAfksaq2aafzoZXEuwKI7wDe4c1F8AY="
    book = zipfile.ZipFile("ogibook.zip").read("ogibook.epub",bytes(pw,"ascii"))
    print(type(book))
    
    key = "5Mm13Gc1iRLy5ukPYRXrwVXYgKLmBFbjPjyVF8ntdCo="
    #offlinekey = Fernet.generate_key()
    cipher_suite = Fernet(key)
    pw = b"gAAAAABfizzjPLF0CYNvBom-CLWpKGh_CHUqW2dVBZDWyB_M330W4IxiVDNUZhMFbVVdgcGkIKOtxyBWu-eIDYVXsy9TZmnvJw"
    p = b'gAAAAABfiz1Hwe4_ZhkZ_JOivju7-gxkuyDqEv_M4ZniOOW8_FkEiMyoEwuaI4J4YmTKZc6NT6bYHUTBoIpw8meqyx3Gshu6VVRcOCNd28A0k5b2uRqL1yYOYdu7VGNhzq97iQqZUE6iKxar4nqmniGSSimnsQkZb7IbMNOEFouQ6JdiDpfDTGmx7IUXBkT60c_tZk0ZKfUw4OYlRvjwfXQ8aeF4H1YOmg=='

    #uncipher_text = (cipher_suite.decrypt(pw))
    password = cipher_suite.decrypt(p)
    print(password)
    #plain_text_encryptedpassword = bytes(uncipher_text).decode("utf-8")  # convert to string
    """
    pass
