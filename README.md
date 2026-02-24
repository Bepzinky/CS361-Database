# CS361-Database
Database microservice for CS361 project.

This microservice uses ZeroMQ as its communication pipeline


# Request

1.Create a REQ socket
2.Connect to port
3. Send a JSON request
4. Wait for the JSON response

Sample request to service: 

```
context = zmq.Context()

socket = context.socket(zmq.REQ)

socket.connect("tcp://localhost:5556")

request = {
    "action": "select",
    "table": "users",
    "filters": {
        "id": 1
    }
}

socket.send(json.dumps(request).encode("utf-8"))
```
Action: action to be performed
Table: name of table you want to perform action on
Filters: misc filters

IMPORTANT: 
If action = insert, you MUST provide data field after table to indicate the data to insert

# Recieve
1. Store response from socket
2. Decode JSON response

Sample code for recieving:
```
response_bytes = socket.recv()

response = json.loads(response_bytes.decode("utf-8"))
```

# Diagram

<img width="843" height="864" alt="Screenshot (118)" src="https://github.com/user-attachments/assets/264e9ebc-03ea-4631-b17f-a98348ff986f" />

