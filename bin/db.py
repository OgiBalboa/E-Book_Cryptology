import os
from cryptography.fernet import Fernet
import firebase
import firebase_admin
from firebase_admin import credentials,storage,auth
from firebase_admin import db as db_
import sys
# Fetch the service account key JSON file contents
import base64
# Initialize the app with a service account, granting admin privileges
import time
import pyminizip
sys.path.append(".env")
from config import config

class db:
	def __init__(self):
		cred = credentials.Certificate('.env/marun-bks.json')
		self.firebase = firebase.Firebase(config)
		#self.storage = self.firebase.storage()
		self.auth = self.firebase.auth()
		self.user = None
		self.app = firebase_admin.initialize_app(cred,config)
		self.books = db_.reference("books")
		self.db = db_
		self.students = db_.reference("students")
		self.codes = db_.reference("codes")
		self.storage = storage.bucket()
	def register(self,email,password):
		self.auth.create_user_with_email_and_password(email=email,password=password)
	def sign(self,email,password):
		self.user = self.auth.sign_in_with_email_and_password(email=email,password=password)
	def download_key(self):
		self.storage.blob("admin/admin_key.txt").download_to_filename(os.path.join(os.getcwd(),"admin_key.txt"))
		with open("admin_key.txt","r") as admin_key:
			output = admin_key.read().split("\n")
		os.system("rm admin_key.txt")
		return output
	def upload_book(self,name,path):
		password = self.db.reference("App").get()["unzip_key"]
		book_path = os.path.join(path,name)
		zip_name = os.path.splitext(name)[0]+".zip"
		zip_path = os.path.join(path,zip_name)
		#print(name,"\n",zip_name,"\n",path,"\n",zip_path)
		pyminizip.compress(book_path, None, zip_path ,password, 1)
		self.storage.blob("books/"+zip_name).upload_from_filename(zip_path)
		return True

def permission(db,temp):
	key = db.db.reference("App").get()["key"]
	cipher_suite = Fernet(key)
	with open('.env/permission.bin', 'rb') as file_object:
		for line in file_object:
			encryptedpwd = line
	uncipher_text = (cipher_suite.decrypt(encryptedpwd))
	plain_text_encryptedpassword = bytes(uncipher_text).decode("utf-8") #convert to string
	if plain_text_encryptedpassword == db.download_key()[1]:
		return True
	else:
		return False
if __name__ == "__main__":
	pass