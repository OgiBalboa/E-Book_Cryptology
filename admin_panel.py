from PyQt5 import QtCore, QtGui, QtWidgets, uic
from pylocker import ServerLocker
from cryptography.fernet import Fernet
import logos_rc
import os
from book import Book,code
global library_
import random
library_ = {}
class BookSettings(QtWidgets.QMainWindow):
    def __init__(self,main):
        super(BookSettings, self).__init__()
        uic.loadUi('ui/book_settings.ui', self)
        self.main = main
        self.generate_code_btn.clicked.connect(self.generate_code)
    def set_book(self,name):
        self.code_output.setText("")
        self.book_name.setText(name)
    def generate_code(self):
        new_code = code(self.code_date_edit.text(), self.book_date_edit.text())
        while True:
            if len(self.main.db.codes.order_by_child('code').equal_to(new_code()).get().items()) > 0: # KOD AYNIYSA YENİ
                new_code = code(self.code_date_edit.text(), self.book_date_edit.text())
            else: break
        self.code_output.setText(new_code())

        info = {new_code():{
            "c_book":self.book_name.text(),
            "code":new_code.text,
            "date": new_code.date,
            "book_date":new_code.book_date,
            "user": new_code.user,
        }
        }
        self.main.db.codes.update(info)
class AdminLibrary(QtWidgets.QMainWindow):
    def __init__(self,main):
        super(AdminLibrary, self).__init__()
        uic.loadUi('ui/library.ui', self)
        self.main = main
        self.add_book()

        self.book_settings = BookSettings(self.main)
        self.tableWidget.doubleClicked.connect(self.open_settings)
    def open_settings(self):
        self.book_settings.set_book(self.tableWidget.selectedItems()[0].data(0))
        self.book_settings.show()
    def add_book(self,):
        if not self.main.online: return
        for book in self.main.db.books.get().items():
            date = "None"
            book = book[1]
            users = "Kimse"
            library_.update({book["name"]:Book(book["name"],book["supervisor"],book["lecture"],date,users)})
        #db.storage.blob("books/"+name+".epub").download_to_filename(os.path.join(os.getcwd(),"res","lib",name+".epub"))
        self.check_library()
    def check_library(self,):
        global library_
        while self.tableWidget.rowCount() > 0:
            self.tableWidget.removeRow(0);
        for row,book in enumerate(library_.values()):
            self.tableWidget.insertRow(row)
            self.tableWidget.setItem(row,0,QtWidgets.QTableWidgetItem(book.name))
            self.tableWidget.setItem(row,1,QtWidgets.QTableWidgetItem(book.lecture))
            self.tableWidget.setItem(row,2,QtWidgets.QTableWidgetItem(book.supervisor))
            self.tableWidget.setItem(row,3,QtWidgets.QTableWidgetItem(book.users))

class AdminPanel(QtWidgets.QMainWindow):
    def __init__(self,main):
        super(AdminPanel, self).__init__()
        uic.loadUi('ui/admin_panel.ui', self)
        self.new_book_btn.clicked.connect(self.new_book)
        self.shelve_btn.clicked.connect(self.open_library)
        self.main = main

        self.library_gui = AdminLibrary(self.main)
        self.new_book_gui = AddBook(self.main)

    def new_book(self):
        self.new_book_gui.show()
    def open_library(self):
        self.main.thread_work(self.library_gui.add_book(),True)
        self.library_gui.show()
class AddBook(QtWidgets.QMainWindow):
    def __init__(self,main):
        super(AddBook, self).__init__()
        uic.loadUi('ui/add_book.ui', self)
        self.ok_btn.clicked.connect(self.submit)
        self.cancel_btn.clicked.connect(self.close)
        self.add_file_btn.clicked.connect(self.add_file)
        self.main = main
    def submit(self):
        if self.check_inputs() != True:
            return
        self.retrieve_info()
        self.main.db.books.update(self.info)
        path = os.path.split(self.file_path_lbl.text())
        self.main.thread_work(lambda: self.main.db.upload_book(path[1],path[0]),True)
        self.reset_inputs()
    def check_inputs(self):
        if self.book_name_input.text() != "" and self.supervisor_input.text() != "" and self.lecture_input.text() != "" \
            and self.file_path_lbl.text() != "": return True
        else: return False

    def retrieve_info(self):
        self.info = {self.book_name_input.text():{
            "name":self.book_name_input.text(),
            "lecture":self.lecture_input.text(),
            "code": self.book_name_input.text().lower().lower().replace(" ","_"),
            "supervisor": self.supervisor_input.text(),
        }
        }
    def reset_inputs(self):
        self.book_name_input.setText("")
        self.supervisor_input.setText("")
        self.lecture_input.setText("")
        self.file_path_lbl.setText("")
    def add_file(self):
        self.file_path = QtWidgets.QFileDialog.getOpenFileName(self, 'Kitap Dosyasını Seçiniz','', "Kitap(*.epub *.pdf *docx);;Tümünü Göster(*)")
        self.file_path_lbl.setText(self.file_path[0])
if __name__ == "__main__":
    pass