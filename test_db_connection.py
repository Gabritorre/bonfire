from psycopg2 import pool
from config import connection_string

# Create a connection pool
connection_pool = pool.SimpleConnectionPool(
	1,  # Minimum number of connections in the pool
	10,  # Maximum number of connections in the pool
	connection_string.render_as_string(hide_password = False)
)

# Check if the pool was created successfully
if connection_pool:
	print("Connection pool created successfully")

# Get a connection from the pool
conn = connection_pool.getconn()

cur = conn.cursor()

# Execute SQL commands to retrieve the current time and version from PostgreSQL
cur.execute('SELECT NOW();')
time = cur.fetchone()[0]

cur.execute('SELECT version();')
version = cur.fetchone()[0]

# Close the cursor and return the connection to the pool
cur.close()
connection_pool.putconn(conn)

# Close all connections in the pool
connection_pool.closeall()

print('Current time:', time)
print('PostgreSQL version:', version)