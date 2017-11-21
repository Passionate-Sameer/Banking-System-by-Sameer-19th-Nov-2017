import threading, datetime, sqlite3, time, re

class User(object):
    
    def __init__(self, name):
        self.accnt_name = name
        self.accnt_num = int(datetime.datetime.now().strftime("%y%m%d%H%M%S"))
        self.debit = float('%.2f' %float(0))
        self.credit = float('%.2f' %float(0))
        self.accnt_bal = float('%.2f' %float(0))
        self.create_user_specific_db()

    def create_user_specific_db(self):
        cur.execute("INSERT INTO Bank_db VALUES (?,?)",(self.accnt_name, self.accnt_num))
        user_acc_num = "_".join(self.accnt_name.split()) + "_" + str(self.accnt_num)
        user_named_db = "CREATE TABLE " + user_acc_num + \
        " (ID INTEGER PRIMARY KEY AUTOINCREMENT, Date TEXT, Time TEXT, Debit REAL, Credit REAL, Balance REAL)"
        cur.execute(user_named_db)
        date, time = date_time()
        initialize_userdb = "INSERT INTO " + user_acc_num + " (Date, Time, Debit, Credit, Balance) VALUES (?,?,?,?,?)"
        cur.execute(initialize_userdb,(date, time, self.debit, self.credit, self.accnt_bal))
        connection.commit()
        print("New account with account number: %d created." %self.accnt_num)
        
    @classmethod
    def from_input(cls):
        while True:
            name = input("Please enter account name (First [Middle] Last): ").upper()
            if len(name) < 1: continue
            acc_name = " ".join(name.split()) #To remove extra spaces
            if check_account_name(acc_name):
                break
        return cls(acc_name)


    def __repr__(self):
        return str(self.name)+ "_Obj"
            
    def __str__(self):
        return str(self.name)


def create_new_user():

    #Creates a new user account
    user = User.from_input()        #Creating user named instance through class method
    input("\nPress Enter to continue... ")

def check_existing_user():

    #calls check_if_user_exists and based on the return value calls menu_2
    ret_val, ac_nam_num = check_if_user_exists()
    if ret_val: menu_2(ac_nam_num)

def check_if_user_exists():

    #Checks if user account exists
    for _ in range(3):
        try:
            acc_number = input("\nPlease enter account NUMBER: ")
            if len(acc_number) < 1: continue
            elif len(acc_number) != 12:
                print("\n\nInvalid Account Number!\n")
            else:
                acc_number = int(acc_number)
                break
        except:
            print("\n\nInvalid Account Number!\n")
            input("\nPress Enter to continue... ")
            
    cur.execute("SELECT Account_name, Account_number FROM Bank_db WHERE Account_number = ?", (acc_number,))
    details = cur.fetchall()
    if len(details) == 0:
        print("\n\nAccount Number does not exist!\n")
        input("Press Enter to continue... ")
        return (False, None)
    else:
        acc_name_from_db = details[0][0]
        acc_number_from_db = details[0][1]
   
    if acc_number != acc_number_from_db:
        print("\n\nAccount does not exist!\n\n")
        input("Press Enter to continue... ")
        return (False, None)

    for _ in range(3):
        aname = input("Please enter account NAME: ").upper()
        if len(aname) < 1: continue
        acc_name = " ".join(aname.split())
        break

    if check_account_name(acc_name):
        if acc_name != acc_name_from_db:
            print("\n\nAccount name does not match with the account number!\n\n")
            input("Press Enter to continue... ")
            return (False, None)
        else:
            user_acc_num = "_".join(acc_name.split()) + "_" + str(acc_number)
            return (True, user_acc_num)
    return (False, None)


def check_account_name(name):

    #Checks the account name for any numbers and special characters
    if re.search(r'[^a-zA-Z\s]', name):
        if re.search(r'[0-9]', name) and re.search(r'[^a-zA-Z0-9\s]', name):
            print("Numbers and Special characters found!\n")
            return False
        else: 
            if re.search(r'[0-9]', name):
                print("Numbers found!\n")
                return False
            if re.search(r'[^a-zA-Z0-9\s]', name):
                print("Special characters found!\n")
                return False
        input("\nPress enter to continue...")
    else:
        return True  


def check_balance(account_name_num):

    #Fetches the balance amount from the account
    balance_check_string = "SELECT Balance FROM " + account_name_num + " ORDER BY ID DESC LIMIT 1"
    cur.execute(balance_check_string)
    balance = cur.fetchone()[0]
    return float(balance)


def check_entered_amount():

    #Gets the amount from the standard input
    while True:
        try:
            amount = input("Enter the amount (press enter to exit): ")
            if len(amount) < 1: break
            elif float(amount) < 0:
                print("Invalid input!")
                continue
            amount = float('%.2f' %float(amount))
            return (True, amount)
        except ValueError:
            print("Invalid input!")    
    return (False, 0)


def credit(account_name_num):

    #Adds the entered amount to the user account
    ret, amount = check_entered_amount()
    if ret:
        credit_amount = float(amount)
        balance = check_balance(account_name_num)
        date, time = date_time()
        update_credit = "INSERT INTO " + account_name_num + " (Date, Time, Debit, Credit, Balance) VALUES (?,?,?,?,?)"
        cur.execute(update_credit,(date, time, 00.00, credit_amount, (balance+credit_amount)))
        connection.commit()
        print("Rs. %.2f deposited to the account" %credit_amount)
        input("\nPress Enter to continue... ")
    return


def debit(account_name_num):

    #Adds the entered amount to the user account
    balance = check_balance(account_name_num)
    while True:
        ret, amount = check_entered_amount()
        if ret:
            debit_amount = float(amount)
            if debit_amount > balance:
                print("Insufficient balance!")
                input("\nPress Enter to continue... ")
                continue
            else:
                date, time = date_time()
                update_credit = "INSERT INTO " + account_name_num + " (Date, Time, Debit, Credit, Balance) VALUES (?,?,?,?,?)"
                cur.execute(update_credit,(date, time, debit_amount, 00.00, (balance-debit_amount)))
                connection.commit()
                print("Rs. %.2f deducted from the account" %debit_amount)
                input("\nPress Enter to continue... ")
        break
    return

def display_statement(user_acc_num):

    #Fetches the last 10 transactions and displays it on standard output
    balance_check_string = "SELECT * FROM " + user_acc_num + " ORDER BY ID DESC LIMIT 10"
    cur.execute(balance_check_string)
    balance = cur.fetchall()
    acc_num = user_acc_num.split("_")[-1]
    acc_nam = " ".join(user_acc_num.split("_")[0:-1])
    print("\nAccount Name: {0:37s} Account Number: {1:12s}".format(acc_nam, acc_num))
    print("="*80)
    print("{0:>10s}{1:>18s}{2:>20s}{3:>16s}{4:>16s}".format("Date", "Time", "Debit", "Credit", "Balance"))
    print("="*80)
    flag = True
    for amt in balance:
        print("{0:>15s} {1:>15s} {2:15.2f} {3:15.2f} {4:15.2f}".format(amt[1], amt[2], amt[3], amt[4], amt[5]))
        if flag: bal = amt[5]
        flag = False
    print("="*80)
    cb = "Closing Balance:"
    print("{0:>64s} {1:15.2f}".format(cb, bal))
    input("\nPress Enter to continue...")

def date_time():
    date = str(datetime.datetime.today().strftime('%d %B %Y'))
    time = str(datetime.datetime.today().strftime('%I:%M:%S %p'))
    return (date, time)
        
def menu_2(user_acc_num):

    #Displays the second menu screen
    while True:
        print('\n'*28)
        print("\n*** WELCOME %s ***" %(" ".join(user_acc_num.split("_")[0:-1])))
        print("Please choose from the following options:")
        print("1. Deposit money")
        print("2. Withdraw money")
        print("3. Check Balance")
        print("4. View Statement")
        print("5. Back to the main screen")

        try:
            choice = int(input("\nPlease select your choice: "))
        except ValueError:
            print("Invalid input!")
            input("\nPress Enter to continue... ")
            continue
        
        if int(choice) == 1:
            credit(user_acc_num)
            
        elif int(choice) == 2:
            debit(user_acc_num)

        elif int(choice) == 3:
            print("\nCurrent Balance is Rs.", check_balance(user_acc_num))
            input("\nPress Enter to continue... ")

        elif int(choice) == 4:
            display_statement(user_acc_num)

        elif int(choice) == 5:
            return

        else:
            print("Selection out of range")
            input("\nPress Enter to continue... ")


if __name__ == "__main__":

    #Starting of the Program
    connection = sqlite3.connect("Users_db.sqlite")
    cur = connection.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS Bank_db (Account_name VARCHAR(50), Account_number INTEGER)")
    while True:  
        print('\n'*28)
        print("!!! Welcome to the Bank of Noida !!!")
        print("\n\n*** MAIN SCREEN ***\nPlease select the type of user:")
        print("1. New User")
        print("2. Existing User")
        choice = input("\nPlease enter your choice (press enter to exit): ")
        try:
            if len(choice) < 1:
                string = "\nThank You for banking with us.\n\n"
                for char in string:
                    print(char, end="")
                    time.sleep(0.03)
                break

            elif int(choice) == 1:
                new_user_thread = threading.Thread(target=create_new_user())
                new_user_thread.start()
                new_user_thread.join()

            elif int(choice) == 2:
                existing_user_thread = threading.Thread(target=check_existing_user())
                existing_user_thread.start()
                existing_user_thread.join()

            else:
                print("Invalid Input! - 1")
                input("\nPress Enter to continue... ")

        except ValueError:
            print("Invalid Input! - 2")
            input("\nPress Enter to continue... ")
    cur.close()







