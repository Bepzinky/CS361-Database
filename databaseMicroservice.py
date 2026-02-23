import mysql.connector # connect to mysql server
import zmq # ZeroMQ
import json
import signal
import sys

def get_connection():
    conn = mysql.connector.connect(
        host='', # add host
        user='', # add username
        password='', # add password
        database='' # add database name
    )
    cursor = conn.cursor(dictionary=True)
    return conn, cursor

# Insert data into database
def insertQuery(req):
    table = req["table"]

    data = req["data"]

    conn, cursor = get_connection()

    columns = ", ".join(data.keys())
    temp = ", ".join(["%s"] * len(data))
    vals = tuple(data.values())

    query = f"INSERT INTO {table} ({columns}) VALUES ({temp})"

    cursor.execute(query, vals)
    conn.commit()

    result = {"rows_affected": cursor.rowcount}

    cursor.close()
    conn.close()

    return result

# Get data from database
def selectQuery(req):
    table = req["table"]

    filters = req.get("filters", {})

    conn, cursor = get_connection()

    where = ""
    vals = ()

    if filters: 
        condition = [f"{i} = %s" for i in filters]
        where = "WHERE " + " AND ".join(condition)
        vals = tuple(filters.values())

    query = f"SELECT * FROM {table} {where}"

    cursor.execute(query, vals)
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return {
        "rows": rows,
        "count": len(rows)
    }

# Update an entry in the database
def updateQuery(req):
    table = req["table"]

    data = req["data"]
    filters = req.get("filters", {})

    conn, cursor = get_connection()

    set_clause = ", ".join([f"{i} = %s" for i in data])
    vals = list(data.values())

    if filters:
        where_clause = "WHERE " + " AND ".join([f"{i} = %s" for i in filters])
        vals += list(filters.values())
    else:
        where_clause = ""

    query = f"UPDATE {table} SET {set_clause} {where_clause}"

    cursor.execute(query, vals)
    conn.commit()

    result = {"rows_affected": cursor.rowcount}

    cursor.close()
    conn.close()
    
    return result

# Delete an entry in the database
def deleteQuery(req):
    table = req["table"]
    filters = req.get("filters", {})

    conn, cursor = get_connection()

    vals = []

    if filters:
        where_clause = "WHERE " + " AND ".join([f"{i} = %s" for i in filters])
        vals = list(filters.values())
    else:
        where_clause = ""

    query = f"DELETE FROM {table} {where_clause}"

    cursor.execute(query, vals)
    conn.commit()

    result = {"rows_affected": cursor.rowcount}

    cursor.close()
    conn.close()

    return result

# Call functions based on action in request
def reqRoute(req):
    action = req.get("action")

    if action == "insert":  
        return insertQuery(req)
    elif action == "select":
        return selectQuery(req)
    elif action == "update":
        return updateQuery(req)
    elif action == "delete":
        return deleteQuery(req)
    else:
        raise ValueError(f"Unknown action: {action}")
    
def signal_handler(sig, frame):
    global socket, context
    print("\nServer Closing...")
    if 'socket' in globals():
        socket.close()
    if 'context' in globals():
        context.term()
    print("Server closed")
    sys.exit(0)

def runServer():
    global context, socket
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5556")

    signal.signal(signal.SIGINT, signal_handler)

    print("Service running on port 5556...")

    while True:
        message = socket.recv()
        request = json.loads(message.decode("utf-8"))
        result = reqRoute(request)
        response = {
            "status": "success",
            "data": result
        }
        socket.send(json.dumps(response).encode("utf-8"))

if __name__ == "__main__":
    runServer()