import re

class User :
    def __init__(self, account_name, first_name, last_name, email, password, phone_number, is_private_account, location) :
        
        self.error = []
        self.valid = True
        
        #user name validation
        if account_name == "" :
            self.valid = False
            self.error.append("Account name cannot be empty")
        else :
            self.account_name = account_name

        #first name validation
        if first_name == "" :
            self.valid = False
            self.error.append("First name cannot be empty")
        else :
            self.first_name = first_name
            self.last_name = last_name

        #email validation
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if(re.fullmatch(regex, email)):
            self.email = email
        else:
            self.valid = False
            self.error.append("Invalid email")

        #password validation
        if len(password) < 8 :
            self.valid = False
            self.error.append("Password too short")
        else :
            self.password = password

        #phone number validation
        if phone_number == "" :
            self.valid = False
            self.error.append("Phone number cannot be empty")
        else :
            self.phone_number = phone_number

        # is_private_account validation
        if is_private_account == "" :
            self.valid = False
            self.error.append("Is private account cannot be empty")
        else :
            self.is_private_account = is_private_account

        #location validation
        if location == "" :
            self.valid = False
            self.error.append("Location cannot be empty")
        else :
            self.location = location

    