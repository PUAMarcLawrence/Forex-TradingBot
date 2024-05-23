import subprocess
currencies = ["EURUSD", "GBPUSD", "AUDUSD","USDCHF", "USDJPY"]
from modules.sqlite_functions import database_initialize, login_retrieve
from modules.mt5_functions import *
venv_python = r'.venv\Scripts\python.exe'

#Bot Start UP
database_initialize(currencies)
if login_retrieve() != None:
    initializeMT5()
while login_retrieve() == None:
    print("No Account in Database")
    userData = input("Enter user ID: ")
    userPass = input("Password: ")
    print("Select which server: \n [1]OctaFX-Demo \n [2]OctaFX-Real2 \n [3]OctaFX-Real")
    while True:
        serverSelect = input("Enter number: ")
        if serverSelect == '1':
            serverData = 'OctaFX-Demo'
            break
        elif serverSelect == '2':
            serverData = 'OctaFX-Real2'
            break
        elif serverSelect == '3':
            serverData = 'OctaFX-Real'
            break
        else:
            print("INVALID INPUT")
    if newUser(userData,userPass,serverData): 
        break

# Start the first program
p1 = subprocess.Popen([venv_python, "forextradebotv3\TradingB_BackEnd.py"])
# Start the second program
p2 = subprocess.Popen([venv_python, "forextradebotv3\TradingB_FrontEnd.py"])

# Wait for both programs to complete
p1.wait()
p2.wait()