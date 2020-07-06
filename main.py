"""
Bu uygulama Marmara Üniversitesi Teknoloji Fakültesi Mekatronik Mühendisliği
Bölümü için geliştirilmiştir. E-book kitapları için şifreleme sistemidir.
E-book okuyucu uygulama Lector ' a teşekkürlerimizle.

@yazar: ogibalboa
Tarih : 05.06.2020
"""
from PyQt5 import QtCore, QtGui, QtWidgets
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
class Auth(Ui_MainWindow):
	def __init__(self,window):
		self.setupUi(window)
		self.submit_button.clicked.connect(self.submit)
		self.register_button.clicked.connect(self.register_page)
		self.register_frame.setHidden(True)
		self.reg_submit_button.clicked.connect(self.register)
		self.reg_cancel_button.clicked.connect(self.back)
	def back(self):
		self.register_frame.setHidden(True)
		self.signIn_frame.setHidden(False)
	def register_page(self):
		self.register_frame.setVisible(True)
		self.signIn_frame.setHidden(True)
	def check_inputs(self,hint = None):
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
		email = self.username_input.text() + "@gmail.com"
		if db.sign(email =email ,password = self.password_input.text()) == None:
			os.system("python ./lector/__main__.py")
	def register(self):
		if self.check_inputs(hint=  "register") == False:
			print("olmadi")
	
			return False
		email = self.reg_username_input.text() + "@gmail.com"
		print(db.register(email = email ,password=self.reg_password_input.text()))
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    mainwin = QtWidgets.QMainWindow()
    ui = Auth(mainwin)
    mainwin.show()
    sys.exit(app.exec_())
