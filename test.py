import sqlite3

# Connect to the database
conn = sqlite3.connect('player.db')
cursor = conn.cursor()

# Add a JSON column "league" to the 'users' table
cursor.execute('ALTER TABLE users ADD COLUMN league JSON')

# Commit the changes and close the connection
conn.commit()
conn.close()