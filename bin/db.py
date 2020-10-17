import os
from cryptography.fernet import Fernet
import firebase
import firebase_admin
from firebase_admin import credentials,storage,auth
from firebase_admin import db as db_
import sys
import zipfile
# Fetch the service account key JSON file contents
import base64
# Initialize the app with a service account, granting admin privileges
import time
import json
import pyminizip
sys.path.append(".env")
import shutil
class db:
	def __init__(self,):
		self.checkDocuments()
		self.offline_key = "5Mm13Gc1iRLy5ukPYRXrwVXYgKLmBFbjPjyVF8ntdCo="

		with open(os.path.join(self.documents_path, "offpwscrt.bin"), "r") as okey:
			self.offline_pass_encrypted = okey.read()
		self.offline_pw = decyrpt(self.offline_pass_encrypted,self.offline_key)
		i = 0
		for item in self.open_zip("marun-bks.zip",["config.json","marun-bks.json"]):
			with open(item,"r") as file:
				if i == 0:config = json.load(file)
				else: marun_bks_json = json.load(file)
				i+=1
		cred = credentials.Certificate(marun_bks_json)
		self.firebase = firebase.Firebase(config)
		#self.storage = self.firebase.storage()
		self.auth = self.firebase.auth()
		self.user = None
		self.app = firebase_admin.initialize_app(cred,config)
		self.books = db_.reference("books")
		self.db = db_
		self.unzip_key = self.db.reference("App").get()["unzip_key"]
		self.students = db_.reference("students")
		self.codes = db_.reference("codes")
		self.storage = storage.bucket()
		self.main = None
	def open_zip(self,dest,files):
		for filename in files:
			yield zipfile.ZipFile(dest).extract(filename,self.documents_path,self.offline_pw)
			os.remove(os.path.join(self.documents_path,filename))
	def register(self,email,password):
		self.auth.create_user_with_email_and_password(email=email,password=password)
	def sign(self,email,password):
		self.user = self.auth.sign_in_with_email_and_password(email=email,password=password)
	def download_key(self):
		with open(os.path.join(self.documents_path,"offpwscrt.bin"),"w") as opas:
			opas.write(self.db.reference("App").get()["offline_pw_encrypted"])
		path = os.path.join(self.documents_path,"admin_key.txt")
		self.storage.blob("admin/admin_key.txt").download_to_filename(path)
		with open(path,"r") as admin_key:
			output = admin_key.read().split("\n")
		os.remove(path)
		return output
	def upload_book(self,name,path):

		book_path = os.path.join(path,name)
		zip_name = os.path.splitext(name)[0]+".zip"
		zip_path = os.path.join(path,zip_name)
		#print(name,"\n",zip_name,"\n",path,"\n",zip_path)
		pyminizip.compress(book_path, None, zip_path ,self.unzip_key, 1)
		self.storage.blob("books/"+zip_name).upload_from_filename(zip_path)
		return True
	def checkDocuments(self):
		self.documents_path = os.path.join(os.path.expanduser("~"), ".marun_bks")
		if not os.path.exists(self.documents_path): os.mkdir(self.documents_path)
		if not os.path.exists(os.path.join(self.documents_path,"library")): os.mkdir(os.path.join(self.documents_path,"library"))
		if not os.path.exists(os.path.join(self.documents_path,"permission.bin")):shutil.copyfile("permission.bin",os.path.join(self.documents_path,"permission.bin"))
		if not os.path.exists(os.path.join(self.documents_path, "offpwscrt.bin")): shutil.copyfile("offpwscrt.bin", os.path.join(self.documents_path, "offpwscrt.bin"))

class db_offline():
	def __init__(self):
		self.documents_path = os.path.join(os.path.expanduser("~"), ".marun_bks")
		self.main = None
		self.books = []
		self.rememberme = False
		self.offline_key = "5Mm13Gc1iRLy5ukPYRXrwVXYgKLmBFbjPjyVF8ntdCo="
	def retrieve_info(self):
		try:
			self.user_info = zipfile.ZipFile(os.path.join(self.documents_path,"user.zip")).read("user.txt",
															self.offline_pw).splitlines()
			self.books = zipfile.ZipFile(os.path.join(self.documents_path,"books.zip")).read("books.txt",
													self.offline_pw).splitlines()
			for i in range(len(self.user_info)):
				self.user_info[i] = self.user_info[i].decode('utf-8')
			for i in range(len(self.books)):
				self.books[i] = self.books[i].decode('utf-8')
			self.unzip_key = self.user_info[3]
			if self.user_info[4] == "True": self.rememberme = True
		except Exception as e : self.main.setWaiting(True,"İnternet Bağlantısını kurduğunuzdan emin olun \n\n HATA Mesajı:\n"+str(e))
		self.user = None
	def save_user_info(self,info):
		user_txt_path = os.path.join(self.documents_path,"user.txt")
		zip_path = os.path.join(self.documents_path,"user.zip")
		with open (user_txt_path,"w") as user_txt:
			user_txt.writelines("\n".join(info))
		pyminizip.compress(user_txt_path,None,zip_path,self.offline_pw,1)
		os.remove(user_txt_path)
	def save_book_info(self,info):
		books_txt_path = os.path.join(self.documents_path, "books.txt")
		books_zip_path = os.path.join(self.documents_path, "books.zip")
		inf = []
		with open(books_txt_path, "w") as books_txt:
			for book in info:
				inf.append(book.get_vals())
			books_txt.write("\n".join(inf))
		pyminizip.compress(books_txt_path,None,books_zip_path,self.offline_pw,1)
		os.remove(books_txt_path)
	def login(self,mail,pw):
		try:
			self.retrieve_info()
			if mail == self.user_info[0] and pw == self.user_info[1]: return True
			else : return False
		except: return False
	def setRememberme(self,status):
		self.rememberme = status
		if status :  self.user_info[4] = "True"
		else	  :	self.user_info[4] = "False"
		self.save_user_info(self.user_info)

	def checkDocuments(self):
		self.documents_path = os.path.join(os.path.expanduser("~"), ".marun_bks")
		if not os.path.exists(self.documents_path): os.mkdir(self.documents_path)
		if not os.path.exists(os.path.join(self.documents_path,"library")): os.mkdir(os.path.join(self.documents_path,"library"))
		if not os.path.exists(os.path.join(self.documents_path,"permission.bin")):shutil.copyfile("permission.bin",os.path.join(self.documents_path,"permission.bin"))
		if not os.path.exists(os.path.join(self.documents_path, "offpwscrt.bin")): shutil.copyfile("offpwscrt.bin", os.path.join(self.documents_path, "offpwscrt.bin"))
def permission(db,temp):
	key = db.db.reference("App").get()["key"]
	with open(os.path.join(db.documents_path,"permission.bin"), 'rb') as file_object:
		for line in file_object:
			passkey = decyrpt(line,key).decode("utf-8")
	if passkey == db.download_key()[1]:
		return True
	else:
		return False
def decyrpt(ms,key):
	if type(ms) != bytes:
		ms = bytes(ms,"ascii")
	cipher_suite = Fernet(key)
	uncipher_text = (cipher_suite.decrypt(ms))
	return bytes(uncipher_text)

def permission_offline():
	pass
if __name__ == "__main__":
	pass
