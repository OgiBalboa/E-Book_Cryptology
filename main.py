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
import pyminizip
import tempfile
from functools import partial
db = db()
if permission(db,"temp") == False:
    exit()
#lock = ServerLocker(password = 
global library
library = {}

class MainMenu(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainMenu,self).__init__()
        uic.loadUi('ui/mainmenu.ui',self)

        self.threadpool = QtCore.QThreadPool()

        #self.threadpool.start(self.worker)
        #self.worker.signals.user_video.connect(self.upd_user)

        self.admin_panel = None
        self.email = ""
        self.no = 0
        self.password = ""
        self.library_path = os.path.join(os.getcwd(), "res", "lib")
        self.dlg = WaitDialog()

        self.add_book_btn.clicked.connect(lambda: self.add_book(self.code_input.text()))
        self.openbook_btn.clicked.connect(self.open_book)
        self.open_admin_panel_btn.clicked.connect(self.open_admin_panel)

        self.refresh_btn.clicked.connect(self.update_library)
        self.open_admin_panel_btn.hide()
        self.admin = False
        self.db = db
        self.flag = False
        self.dlg.close()
        self.temp = tempfile.TemporaryDirectory()
        self.thread_work(lambda: self.unzip_books())
    def submit(self):
        user_info = db.students.child(self.no).get()
        if user_info["secret"] == "admin":
            self.admin = True
            self.open_admin_panel_btn.show()
            self.update_library()
        self.db.st_books = self.db.db.reference("students/" + self.no + "/st_books")

    def open_book(self):
        name = self.tableWidget.selectedItems()[0].data(0)+".epub"
        cpath = os.getcwd()
        path = os.path.join(self.temp,name)
        os.system('sumatra -restrict -view "single page" "' + path +'"')
    def update_library(self):
        try:
            for book in db.students.child(self.no).child("st_books").get().items():

                info = db.books.child(book[0]).get()
                if info == None:
                    continue
                date = book[1]
                library.update({book: Book(info["name"], info["supervisor"], info["lecture"],
                                           date)})
        except Exception as e: print(e)
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

            self.thread_work(lambda : db.storage.blob("books/"+name+".zip").download_to_filename(os.path.join(self.library_path,name+".zip")),True)
        self.unzip(book["name"]+".zip")
        self.db.st_books.update({name:date})
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
    def setWaiting(self,status: bool,text = "İşlem Sürüyor Lütfen Bekleyiniz..."):
        if status == True:
            self.dlg.show_(text,"Lütfen Bekleyin")
        else:
            self.dlg.close()
    def thread_work (self,func,dlg = None,hint = None):
        worker = server_worker(self)
        if dlg: worker.signals.finished.connect(self.setWaiting)
        if hint == "unzip": worker.signals.finished.connect(self.flag_)
        worker.func = func
        self.threadpool.start(worker)
    def flag_(self,status):
        self.flag = status

    def unzip(self, book):
        password = self.db.db.reference("App").get()["unzip_key"]
        name = os.path.splitext(book)[0]
        source_file = os.path.join(self.library_path, book)
        dest_file = os.path.join(self.temp.name, name + ".epub")
        try: pyminizip.uncompress(source_file, password, dest_file, 0)
        except: pass
        os.rename(os.path.join(os.getcwd(), name + ".epub"), dest_file)
    def unzip_books(self,hint =  None):
        for book in os.listdir(self.library_path):
            if book.endswith(".zip"): self.unzip(book)

class WaitDialog(QtWidgets.QDialog):
    def __init__(self):
        super(WaitDialog, self).__init__()
        self.lbl = QtWidgets.QLabel(self)
        self.lbl.setText("Hatalı E-mail veya Şifre!")
        self.btn = QtWidgets.QPushButton('Cancel')
        self.btn.setEnabled(True)
        self.btn.clicked.connect(self.close)
        self.setWindowTitle("Hata!")
        self.resize(250, 50)

    def show_(self, text, title=None):
        self.lbl.setText(text)
        if title != None:
            self.setWindowTitle(title)
        else:
            self.setWindowTitle("Hata!")
        self.show()

class server_signals(QtCore.QObject):
    finished = QtCore.pyqtSignal(object)
    """
    error = pyqtSignal(tuple)
    user_video = pyqtSignal(object)
    guest_video = pyqtSignal(object)
    """
    pass
class server_worker(QtCore.QRunnable):

    #@pyqtSlot()
    def __init__(self,main):
        super(server_worker, self).__init__()
        self.signals = server_signals()
        self.flag = False
        self.main = main
        self.func = None
    def run(self,):
        if self.flag == True:
            return
        else:
            self.flag = True
            self.signals.finished.emit(True)
            if not self.func == None: self.func()
            self.signals.finished.emit(False)
            self.flag = False


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
