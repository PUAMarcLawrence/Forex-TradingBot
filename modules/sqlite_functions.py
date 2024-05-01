import sqlite3
databasename = 'database/login.db'

def database_initialize():
    # Connect to database
    database = sqlite3.connect(databasename)

    # Create a cursor
    cur = database.cursor()
    try:
        # Create a Table
        cur.execute(""" CREATE TABLE login (
                    username number,
                    password text,
                    server text
                    )
                    """)

        # Commit our command
        database.commit()
    except:
        print("table already exists,skipping...")
    
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
