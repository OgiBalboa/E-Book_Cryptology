from PyQt5 import QtCore, QtGui, QtWidgets, uic
from pylocker import ServerLocker
from cryptography.fernet import Fernet
import logos_rc


class AdminPanel(QtWidgets.QMainWindow):
    def __init__(self,main):
        super(AdminPanel, self).__init__()
        uic.loadUi('ui/admin_panel.ui', self)
        self.new_book_btn.clicked.connect(self.new_book)
        self.main = main

        self.new_book_gui = AddBook(self.main)
    def new_book(self):
        self.new_book_gui.show()

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
        print("oldu")
        self.main.db.books.update(self.retrieve_info())
    def check_inputs(self):
        if self.book_name_input.text() != "" and self.supervisor_input.text() != "" and self.lecture_input.text() != "" \
            and self.file_path_lbl.text() != "": return True
        else: return False

    def retrieve_info(self):
        info = {self.book_name_input.text():{
            "name":self.book_name_input.text(),
            "lecture":self.lecture_input.text(),
            "code": self.book_name_input.text().lower().lower().replace(" ","_"),
            "supervisor": self.supervisor_input.text(),
        }
        }
        return info
    def add_file(self):
        self.file_path = QtWidgets.QFileDialog.getOpenFileName(self, 'Kitap Dosyasını Seçiniz','', "Kitap(*.epub *.pdf *docx);;Tümünü Göster(*)")
        self.file_path_lbl.setText(self.file_path[0])
if __name__ == "__main__":
    pass