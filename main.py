"""
Bu uygulama Marmara Üniversitesi Teknoloji Fakültesi Mekatronik Mühendisliği
Bölümü için geliştirilmiştir. E-book kitapları için şifreleme sistemidir.
@yazar: ogibalboa
Tarih : 05.06.2020
"""
import sys
sys.path.append("bin")
from PyQt5 import QtCore, QtGui, QtWidgets,uic
from subprocess import call
import datetime
from db import db,permission
import os
from pylocker import ServerLocker
from cryptography.fernet import Fernet
import logos_rc
from auth import AuthMenu
from admin_panel import AdminPanel
from book import Book
db = db()
if permission(db) == False:
    exit()
#lock = ServerLocker(password = 
global library
library = {}

class MainMenu(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainMenu,self).__init__()
        uic.loadUi('ui/mainmenu.ui',self)
        self.admin_panel = None
        self.email = ""
        self.no = 0
        self.password = ""
        self.add_book_btn.clicked.connect(lambda: self.add_book(self.code_input.text()))
        self.openbook_btn.clicked.connect(self.open_book)
        self.open_admin_panel_btn.clicked.connect(self.open_admin_panel)
        self.refresh_btn.clicked.connect(self.update_library)

        self.open_admin_panel_btn.hide()
        self.admin = False
        self.db = db
        self.dlg = WaitDialog()
        self.dlg.close()
    def submit(self):

        user_info = db.students.child(self.no).get()
        if user_info["secret"] == "admin":
            self.admin = True
            self.open_admin_panel_btn.show()
            self.update_library()
        self.db.st_books = self.db.db.reference("books/" + self.no + "/st_books")
    def open_book(self):
        name = self.tableWidget.selectedItems()[0].data(0)+".epub"
        cpath = os.getcwd()
        path = os.path.join(cpath,"res","lib",name)
        os.system('sumatra -restrict -view "single page" "' + path +'"')
    def update_library(self):
        for book in db.students.child(self.no).child("st_books").get().items():

            info = db.books.child(book[0]).get()
            if info == None:
                continue
            date = book[1]
            library.update({book: Book(info["name"], info["supervisor"], info["lecture"],
                                       date)})
        self.check_library()
    def add_book(self,code):
        name = None
        for item in db.codes.order_by_child('code').equal_to(code).get().items():
            name = item[1]["c_book"]
            date = item[1]["date"]
        for book in db.books.order_by_child('name').equal_to(name).get().items():
            book = book[1]
            library.update({name:Book(book["name"],book["supervisor"],book["lecture"],date)})
        if not name == None:
            db.storage.blob("books/"+name+".epub").download_to_filename(os.path.join(os.getcwd(),"res","lib",name+".epub"))
        self.db.st_books()
        self.check_library()
    def check_library(self,):
        global library
        while self.tableWidget.rowCount() > 0:
            self.tableWidget.removeRow(0);
        for row,book in enumerate(library.values()):
            self.tableWidget.insertRow(row)
            self.tableWidget.setItem(row,0,QtWidgets.QTableWidgetItem(book.name))
            self.tableWidget.setItem(row,1,QtWidgets.QTableWidgetItem(book.lecture))
            self.tableWidget.setItem(row,2,QtWidgets.QTableWidgetItem(book.supervisor))
            self.tableWidget.setItem(row,3,QtWidgets.QTableWidgetItem(book.date))
    def open_admin_panel(self):
        self.admin_panel.show()
    def setWaiting(self,status: bool,text):
        if status == True:
            self.dlg.setTitle(text)
            self.dlg.show()
        else:
            self.dlg.close()

class WaitDialog(QtWidgets.QProgressDialog):
    def __init__(self):
        super(WaitDialog, self).__init__()
        self.setAutoClose(True)
        self.btn = QtWidgets.QPushButton('Cancel')
        self.btn.setEnabled(False)
        self.setCancelButton(self.btn)
    def setTitle(self,text):
        self.setWindowTitle(text)
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("fusion")

    menu = MainMenu()
    auth = AuthMenu(menu)
    admin_panel = AdminPanel(menu)
    menu.admin_panel = admin_panel
    #ui = Auth(mainwin)
    auth.show()
    sys.exit(app.exec_())
