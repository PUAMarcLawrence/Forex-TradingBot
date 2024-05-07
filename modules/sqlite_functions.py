import sqlite3
databasename = 'database/login.db'

def database_initialize(list):
    # Connect to database
    database = sqlite3.connect(databasename)

    # Create a cursor
    cur = database.cursor()
    # Create a Table
    cur.execute(""" CREATE TABLE IF NOT EXISTS login (
                username number,
                password text,
                server text
                )
                """)
    # Commit our command
    database.commit()

    # Create a cursor
    cur = database.cursor()
    my_columns = " NUMBER, ".join(list)
    my_command = "CREATE TABLE IF NOT EXISTS currencies (" + my_columns + " NUMBER)"
    cur.execute(my_command)
    # Commit our command
    database.commit()

    # Create a cursor
    cur = database.cursor()
    cur.execute("SELECT * FROM currencies")
    if cur.fetchone() == None:
        cur.execute("INSERT INTO currencies VALUES (0,0,0,0,0)")
        # Commit our command
        database.commit()
    # close out connection
    database.close()
    return

def login_retrieve():
    # Connect to database
    database = sqlite3.connect(databasename)

    # Create a cursor
    cur = database.cursor()

    cur.execute("SELECT * FROM login")
    accounts = cur.fetchone()
    database.close()
    return accounts

def update_account(ID,password,server):
    # Connect to database
    database = sqlite3.connect(databasename)

    # Create a cursor
    cur = database.cursor()

    cur.execute("SELECT * FROM login")
    if cur.fetchone() == None:
        cur.execute("INSERT INTO login VALUES (" + ID + ", '"+ password +"', '"+ server +"')")
    else:
        # UPDATE
        cur.execute("UPDATE login SET username = "+ ID +",password = '"+ password +"',server = '"+ server +"' WHERE rowid = '1'")

    # Commit our command
    database.commit()

    # close out connection
    database.close()
    return

def update_choice(symbol,choice):
    # Connect to database
    database = sqlite3.connect(databasename)

    # Create a cursor
    cur = database.cursor()
    
    # UPDATE
    command = "UPDATE currencies SET " + symbol + " = " + str(choice) + " WHERE rowid = '1'"
    cur.execute(command)
    
    # Commit our command
    database.commit()

    # close out connection
    database.close()
    return

def choiceRetrieve(symbol):
    # Connect to database
    database = sqlite3.connect(databasename)

    # Create a cursor
    cur = database.cursor()

    cur.execute("SELECT " + symbol + " FROM currencies")
    choices = cur.fetchone()
    database.close()

    return choices[0]
