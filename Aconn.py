import mimetypes
import socket
import threading
from aconn_db import DatabaseAconn
import os

db = DatabaseAconn("sessions.json")

s = socket.socket()

host = "127.0.0.1"
port = 5000

s = socket.socket()
global conn, addr

conn_list = []
addr_list = []


class Request:
    def __init__(self, method, path, values, origin, url_params):
        self.method = method
        self.path = path
        self.values = values
        self.origin = origin
        self.url_params = url_params


def acceptConnections():
    while True:
        s.listen(5)
        global conn, addr
        conn, addr = s.accept()
        print("Connected from " + addr[0])
        conn_list.append(conn)
        addr_list.append(addr)


def sendFile(path):
    file = open(path, "r").read()
    return {"Content Type": mimetypes.MimeTypes().guess_type(path)[0], "Data": file}


def renderHTML(path, data_input=None):
    if data_input is None:
        data_input = {"": ""}
    file = open(path, "r")
    file_data = file.read()
    for i in data_input:
        file_data = file_data.replace("&" + i + "&", str(data_input[i]))

    return {"Content Type": "Content-Type: text/html\n", "Data": file_data}


def createSession(login_user_id, origin):
    if not os.path.exists("sessions.json"):
        db.createDB()

    db.appendToDB({
        "user_id": login_user_id,
        "origin": origin
    })


def loggedIn(origin):
    if len(db.filteredQuery({"origin": origin})) > 0:
        return True
    return False


def getCurrentUser(origin):
    return db.filteredQuery({"origin": origin})[0]


def handleRequests(routes):
    while True:
        for connection in conn_list:
            try:
                receive_req = connection.recv(2048)
                receive_req_list = receive_req.decode("utf-8").split(" ")
                url_params = {}
                if len(receive_req_list[1].split("?")[-1].split("=")) > 1:
                    for i in receive_req_list[1].split("?")[-1].split("&"):
                        url_params[i.split("=")[0]] = \
                            i.split("=")[1]

                req_inst = Request(receive_req_list[0], receive_req_list[1], receive_req_list[-1].split("\r")[-1],
                                   receive_req_list[3], url_params)

                run_req_func = routes.get(receive_req.decode("utf-8").split(" ")[1].split("?")[0])(req_inst)

                connection.send('HTTP/1.0 200 OK\n'.encode())
                connection.send(run_req_func["Content Type"].encode())
                connection.send("\n".encode())
                connection.send(run_req_func["Data"].encode())
                connection.close()
                conn_list.remove(connection)
            except KeyError:
                pass


def startServer():
    s.bind((host, port))
    print(f"Started server at http://{host}:{port}")
    accept_thread = threading.Thread(target=acceptConnections)
    accept_thread.start()
