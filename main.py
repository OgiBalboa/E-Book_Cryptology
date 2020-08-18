"""
Bu uygulama Marmara Üniversitesi Teknoloji Fakültesi Mekatronik Mühendisliği
Bölümü için geliştirilmiştir. E-book kitapları için şifreleme sistemidir.
E-book okuyucu uygulama Lector ' a teşekkürlerimizle.

@yazar: ogibalboa
Tarih : 05.06.2020
"""
from PyQt5 import QtCore, QtGui, QtWidgets,uic
from subprocess import call
import datetime
from db import db,permission
import os
from pylocker import ServerLocker
from cryptography.fernet import Fernet
db = db()
if permission(db) == False:
	exit()
#lock = ServerLocker(password =
global library
library = {}
class Book:
	def __init__(self,name,supervisor,lecture,date):
		self.name = name
		self.supervisor = supervisor
		self.lecture = lecture
		self.date = date
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
		self.openbook_btn.clicked.connect(self.open_book)
	def back(self):
		self.register_frame.setHidden(True)
		self.signIn_frame.setHidden(False)
	def register_page(self):
		self.register_frame.setVisible(True)
		self.signIn_frame.setHidden(True)
	def check_inputs(self,hint = None):
		if self.password_input.text() == "":
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
		elif self.password_input.text() == "":
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
	def open_book(self):
		name = self.tableWidget.selectedItems()[0].data(0)
		cpath = os.getcwd()
		os.system("sumatra -restrict -view 'single page' " + os.path.join(cpath,"res","lib",name+".epub"))
		
	def add_book(self,code):
		for item in db.codes.order_by_child('code').equal_to(code).get().items():
			name = item[1]["c_book"]
			date = item[1]["date"]
		for book in db.books.order_by_child('name').equal_to(name).get().items():
			book = book[1]
			library.update({name:Book(book["name"],book["supervisor"],book["lecture"],date)})
		db.storage.blob("books/"+name+".epub").download_to_filename(os.path.join(os.getcwd(),"res","lib",name+".epub"))
		self.check_library()
	def check_library(self,):
		global library
		print(library)
		print(self.tableWidget.rowCount())
		while self.tableWidget.rowCount() > 0:
			self.tableWidget.removeRow(0);
		for row,book in enumerate(library.values()):
			self.tableWidget.insertRow(row)
			self.tableWidget.setItem(row,0,QtWidgets.QTableWidgetItem(book.name))
			self.tableWidget.setItem(row,1,QtWidgets.QTableWidgetItem(book.lecture))
			self.tableWidget.setItem(row,2,QtWidgets.QTableWidgetItem(book.supervisor))
			self.tableWidget.setItem(row,3,QtWidgets.QTableWidgetItem(book.date))
if __name__ == "__main__":
	import sys
	app = QtWidgets.QApplication(sys.argv)
	app.setStyle("fusion")
	menu = MainMenu()
	#ui = Auth(mainwin)
	menu.show()
	sys.exit(app.exec_())
