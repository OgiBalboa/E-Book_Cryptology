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
from db import db,permission, db_offline, permission_offline, day_difference
import os
from pylocker import ServerLocker
from cryptography.fernet import Fernet
import logos_rc
from auth import AuthMenu
from admin_panel import AdminPanel
from book import Book
import pyminizip
import tempfile
import zipfile
from functools import partial
import requests
global library
library = {}
global supported_filetypes
supported_filetypes = [".pdf",".epub",".docx",".doc"]
class MainMenu(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainMenu,self).__init__()
        uic.loadUi('ui/mainmenu.ui',self)
        self.offline_key ="5Mm13Gc1iRLy5ukPYRXrwVXYgKLmBFbjPjyVF8ntdCo="
        self.threadpool = QtCore.QThreadPool()
        self.admin_panel = None
        self.email = ""
        self.no = 0
        self.password = ""
        self.rememberme = False
        self.documents_path = os.path.join(os.path.expanduser("~"),".marun_bks")
        self.library_path = os.path.join(self.documents_path,"library")
        self.books_at_library = []
        if not os.path.isdir(self.documents_path): os.mkdir(self.documents_path)
        if not os.path.isdir(self.library_path): os.mkdir(self.library_path)
        self.dlg = WaitDialog(self)
        self.add_book_btn.clicked.connect(lambda: self.add_book(self.code_input.text()))
        self.openbook_btn.clicked.connect(self.open_book)
        self.open_admin_panel_btn.clicked.connect(self.open_admin_panel)

        self.refresh_btn.clicked.connect(self.update_library)
        self.open_admin_panel_btn.hide()
        self.admin = False
        self.db = db
        self.offline_pw = self.db.offline_pw
        self.ofdb = db_offline()
        self.flag = False
        self.dlg.close()
        self.temp = tempfile.TemporaryDirectory()
        self.ofdb.main = self
        self.ofdb.offline_pw = self.offline_pw
        if os.path.exists(os.path.join(self.documents_path,"user.zip")): self.ofdb.retrieve_info()
        #self.thread_work(lambda: self.unzip_books())
    def submit(self):
        if self.online():
            self.save_infos()
            user_info = db.students.child(self.no).get()
            if user_info["secret"] == "admin":
                self.admin = True
                self.open_admin_panel_btn.show()
            elif user_info["secret"] == "blocked":
                self.close()
                SystemExit("HATA")
                #sys.exit("HATA SİSTEMDEN ENGELLENDİNİZ")
            print(self.no)
            self.db.st_books = self.db.db.reference("students/" + self.no + "/st_books")
            self.db.student = self.db.db.reference("students/" + self.no)
        self.update_library()
    def open_book(self):
        book = self.tableWidget.selectedItems()[0].data(0)
        ext = os.path.splitext(zipfile.ZipFile(os.path.join(self.library_path,book+".zip")).namelist()[0])[-1]
        name = book + ext
        self.unzip(book+".zip")
        path = os.path.join(self.temp,name)
        os.system('sumatra -restrict -view "single page" "' + path +'"')
        os.remove(path)
    def update_library(self):
        if self.online():
            library.clear()
            try:
                for book in db.students.child(self.no).child("st_books").get().items():

                    info = db.books.child(book[0]).get()
                    if info == None:
                        continue
                    date = book[1]
                    if day_difference(self.login_time,date) < 0:
                        print("Tarihi geçti")
                        continue
                    library.update({book: Book(info["name"], info["supervisor"], info["lecture"], date)})
                    self.save_infos()
                st_books = {}
                for book in library.values():
                    st_books.update({book.name:book.date})
                if st_books == {}: st_books.update({"None":"None"})
                self.db.student.update({"st_books" : st_books})
            except Exception as e: print(e)
            ###***************************** OFFLINE İKEN YAPILACAK İŞLEMLER********************************************************
        else:
            try: self.ofdb.retrieve_info()
            except Exception as e:
                self.setWaiting(True,"Kitaplık verileriniz kayıp, lütfen internet bağlantınızı sağlayın ve uygulamaya tekrar giriş yapın. \n\n HATA Mesajı\n\n"+str(e))
                return
            for book_ in self.ofdb.books:
                book = book_.split(",")
                library.update({book[0]:Book(book[0],book[1],book[2],book[3],book[4])})
                self.ofdb.save_user_info(
                    [self.email, self.password, ".".join([str(self.login_time.day), str(self.login_time.month),
                                                          str(self.login_time.year)]),
                     self.ofdb.unzip_key,
                     str(self.ofdb.rememberme)])
                self.ofdb.save_book_info(library.values())
        self.check_library()
        self.check_local_library()
    def save_infos(self):
        self.ofdb.save_user_info(
            [self.email, self.password, ".".join([str(self.login_time.day), str(self.login_time.month),
                                                  str(self.login_time.year)]),
             self.db.db.reference("App").get()["unzip_key"],
             str(self.ofdb.rememberme)])
        self.ofdb.save_book_info(library.values())
    def add_book(self,code):
        if not self.online(): self.setWaiting(True,"İnternet Bağlantınızı Kontrol Ediniz!")
        try:
            name = None
            for item in db.codes.order_by_child('code').equal_to(code).get().items():
                name = item[1]["c_book"]
                date = item[1]["book_date"]
            for book in db.books.order_by_child('name').equal_to(name).get().items():
                book = book[1]
                library.update({name:Book(book["name"],book["supervisor"],book["lecture"],date)})
            if not name == None:
                try:
                    self.thread_work(lambda : self.db.download_book(name,os.path.join(self.library_path, name + ".zip")),True)
                except : self.setWaiting(True,"Kitabı indirirken bir hata oluştu")
            self.db.st_books.update({name:date})
        except Exception as e:
            print(e)
            self.setWaiting(True,"Kitap Eklenemedi \n\n\nHATA MESAJI\n\n\n"+ str(e))
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
    def check_local_library(self):
        self.books_at_library.clear()
        for book in os.listdir(self.library_path):
            if not book.endswith(".zip"): continue
            self.books_at_library.append(os.path.splitext(book)[0])
        missing_books = set(library.keys()).difference(set(self.books_at_library))
        excess_books = set(self.books_at_library).difference(set(library.keys()))
        print("Lib : {}, missing : {}, excess : {}".format(self.books_at_library,missing_books,excess_books))

        if missing_books or excess_books: self.setWaiting(True, "Kütüphaneniz düzenleniyor, lütfen bekleyiniz...")
        for excess_book in excess_books:
            try: os.remove(os.path.join(self.library_path,excess_book+".zip"))
            except Exception as e: print(e)
        self.setWaiting(False)
        for missing_book in missing_books:
            try:
                self.thread_work(lambda: self.db.download_book(missing_book, os.path.join(self.library_path, missing_book + ".zip")),
                                 True)
                self.setWaiting(False)
            except:
                self.setWaiting(True, "Kütüphanenizde eksik bulunan bir kitabı indirirken bir hata oluştu")
    def open_admin_panel(self):
        self.admin_panel.show()
    def setWaiting(self,status: bool,text = "İşlem Sürüyor Lütfen Bekleyiniz...",title = "DİKKAT!"):
        if status == True:   self.dlg.show_(text,title)
        elif status == None: self.dlg.show_(self.error_message,title)
        else:                self.dlg.close()
    def errormessage(self,error):
        self.error_message = str(error)
    def thread_work (self,func,dlg = None,hint = None):
        worker = server_worker(self)
        if dlg:
            worker.signals.finished.connect(self.setWaiting)
            worker.signals.error.connect(self.errormessage)
        if hint == "unzip": worker.signals.finished.connect(self.flag_)
        worker.func = func
        self.threadpool.start(worker)
    def flag_(self,status):
        self.flag = status

    def unzip(self, book):
        ext = os.path.splitext(zipfile.ZipFile(book).namelist()[0])[-1]
        password = self.db.db.reference("App").get()["unzip_key"]
        name = os.path.splitext(book)[0]
        source_file = os.path.join(self.library_path, book)
        dest_file = os.path.join(self.temp.name, name + ext)
        try: pyminizip.uncompress(source_file, password, dest_file, 0)
        except: pass
        #os.rename(os.path.join(source_file, name + ext), dest_file)
        return
    def unzip_books(self,hint =  None):
        for book in os.listdir(self.library_path):
            if book.endswith(".zip"): self.unzip(book)
    def online(self,):
        try:
            requests.get('http://216.58.192.142', timeout=1)
            self.connection_display.setStyleSheet("background-color: rgb(35, 100, 54);")
            return True
        except Exception as e:
            print(e)
            self.connection_display.setStyleSheet("background-color: rgb(164, 0, 0);")
            return False
class WaitDialog(QtWidgets.QDialog):
    def __init__(self,parent):
        super(WaitDialog, self).__init__(parent)
        self.lbl = QtWidgets.QLabel(self)

        self.lbl.setText("Hatalı E-mail veya Şifre!")
        self.btn = QtWidgets.QPushButton('Cancel')
        self.btn.setEnabled(True)
        self.btn.clicked.connect(self.close)
        self.setWindowTitle("Hata!")
        self.resize(700, 200)

    def show_(self, text, title=None):
        self.lbl.setText(text)
        self.lbl.setAlignment(QtCore.Qt.AlignCenter)
        if title != None:
            self.setWindowTitle(title)
        else:
            self.setWindowTitle("Hata!")
        self.show()

class server_signals(QtCore.QObject):
    finished = QtCore.pyqtSignal(object)
    error = QtCore.pyqtSignal(object)
class server_worker(QtCore.QRunnable):
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
            try    :
                if not self.func == None: self.func()
                self.signals.finished.emit(False)
                self.flag = False
            except Exception as e:
                print(e)
                self.signals.error.emit("Yükleme sırasında bir sorun oluştu, lütfen geliştiriciye ulaşın: info@ogibalboa.com"
                                           "\n\nHATA MESAHI\n\n"+ str(e))
                self.signals.finished.emit(None)


if __name__ == "__main__":
    connection = False
    gate = False
    import sys
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("fusion")
    db = db()
    menu = MainMenu()
    db.main = menu
    try:
        if permission(db, "temp") == False:
            menu.setWaiting(True,"Sunucudan izin alınamadı, lütfen yöneticiye ulaşın : info@ogibalboa.com")
            gate = True
        connection = True
    except Exception as e:
        print(e)
        if permission_offline() == False:
            menu.setWaiting(True,"Sunucudan izin alınamadı, lütfen yöneticiye ulaşın : info@ogibalboa.com")
            gate = True

    auth = AuthMenu(menu)
    admin_panel = AdminPanel(menu)
    menu.admin_panel = admin_panel
    auth.show()
    if gate: auth.close()
    sys.exit(app.exec_())