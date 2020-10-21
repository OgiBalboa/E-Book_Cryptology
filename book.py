import random
import datetime
class Book:
    def __init__(self,name,supervisor,lecture,date,users = "None"):
        self.name = name
        self.supervisor = supervisor
        self.lecture = lecture
        self.date = date
        self.users = users
    def get_vals(self):
        return ",".join([str(self.name),str(self.supervisor),str(self.lecture),str(self.date),str(self.users)])

class code:
    def __init__(self,date,book_date,user = ""):
        self.text = self.generate_code()
        self.date = date
        self.book_date = book_date
        self.user = user
    def generate_code(self,length = 6):
        upper = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'K', 'L', 'M', 'N', 'O', 'P', 'R', 'S', 'T', 'Y', 'Z']
        nums = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
        lower = ['a','b', 'c', 'd', 'e', 'f', 'g', 'h', 'k', 'l', 'm', 'n', 'o', 'p', 's', 'r', 't', 'y', 'z',]
        chars = upper+nums
        out = ""
        for i in range(0, length):
            out += chars[random.randint(0, len(chars) - 1)]
        return out
    def __call__(self, *args, **kwargs):
        return self.text


