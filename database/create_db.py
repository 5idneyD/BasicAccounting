import sqlite3

# Form connection with database.db in database folder
connection = sqlite3.connect("./database/database.db")
cursor = connection.cursor()

# close database once formed
connection.close()

