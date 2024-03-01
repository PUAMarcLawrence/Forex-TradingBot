import sqlite3
databasename = 'database/login.db'

def add_data(username, password):
    # Connect 
    database = sqlite3.connect(databasename)
    # Create cursor
    cur = database.cursor()
    cur.execute("INSERT INTO forex VALUES (?,?)",(username,password))
    # Commit command
    database.commit()
    # Close connection
    database.close()

def login_retrieve():
    database = sqlite3.connect(databasename)

    # Create a cursor
    cur = database.cursor()

    cur.execute("SELECT * FROM login")
    accounts = cur.fetchone()

    # Commit our command
    database.commit()

    # close out connection
    database.close()

    return accounts