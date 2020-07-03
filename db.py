import pyrebase
import os
from cryptography.fernet import Fernet
class db:
	def __init__(self):
		self.config = {
			"apiKey": "AIzaSyACtVeNXkw53Rb2yMHiGWxPRQx9DTseSiQ",
			"authDomain": "marun-bks.firebaseapp.com",
			"databaseURL": "https://marun-bks.firebaseio.com",
			"projectId": "marun-bks",
			"storageBucket": "marun-bks.appspot.com",
			"messagingSenderId": "840842015753",
			"appId": "1:840842015753:web:c20cb7ff67f077d07cf4d8",
			"measurementId": "G-Z2Z9YXSYWX"
		  }
		self.firebase = pyrebase.initialize_app(self.config)
		self.storage = self.firebase.storage()
		self.auth = self.firebase.auth()
	
	def register(self,email,password):
		self.auth.create_user_with_email_and_password(email=email,password=password)
	def sign(self,email,password):
		self.auth.sign_in_with_email_and_password(email=email,password=password)
	def download_key(self):
		self.storage.child("/admin/admin_key.txt").download(os.path.join(os.getcwd(),"admin_key.txt"))
		with open("admin_key.txt","r") as admin_key:
			output = admin_key.read().split("\n")
		os.system("rm admin_key.txt")
		return output			
#db().register("dede@gmail.com","123456")
def permission():
	key = b'pRmgMa8T0INjEAfksaq2aafzoZXEuwKI7wDe4c1F8AY='
	cipher_suite = Fernet(key)
	with open('permission.bin', 'rb') as file_object:
		for line in file_object:
			encryptedpwd = line
	uncipher_text = (cipher_suite.decrypt(encryptedpwd))
	plain_text_encryptedpassword = bytes(uncipher_text).decode("utf-8") #convert to string
	if plain_text_encryptedpassword == db().download_key()[1]:
		return True
	else:
		return False

