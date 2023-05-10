import threading
import socket
import ssl
import signal
import struct

import warnings
import json
from datetime import datetime

signal.signal(signal.SIGINT, signal.SIG_DFL)


class Server:
    def __init__(self, host="localhost", port=1235):
        self.HOST = host
        self.PORT = port
        self.HEADER_LENGTH = 2
        self.connected_users = {}
        self.cipher = "ECDHE-RSA-AES128-GCM-SHA256"

        self.serverCertFile = "server/server.crt"
        self.serverKeyFile = "server/server.key"
        self.clientsCert = "server/clients.pem"

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.HOST, self.PORT))
        self.server_socket.listen(1)
        self.my_ssl_ctx = self.setup_SSL_context()

        self.clients = set()
        self.clients_lock = threading.Lock()

        self.run()


    def run(self):
        print("[system] listening ...")
        
        while True:
            try:
                conn, addr = self.server_socket.accept()
                conn = self.my_ssl_ctx.wrap_socket(conn, server_side=True)

                cert = conn.getpeercert()
                for sub in cert['subject']:
                    for key, value in sub:
                        if key == 'commonName':
                            user = value

                if user in self.connected_users:
                    print(f"[system] {addr[0]}:{addr[1]} tired to login with already used name")
                    self.send_message(conn, {"sender": "System", "message":"FAILED: User already loged in"})
                    continue

                self.send_message(conn, {"sender": "System", "message":"SUCCESS: Sucessful login"})
                self.send_message_to_all(conn, {"sender": "System", "message":f"{user} joined the chat"})

                with self.clients_lock:
                    self.clients.add(conn)

                thread = threading.Thread(target=self.client_thread, args=(conn, addr, user))
                thread.daemon = True
                thread.start()

            except KeyboardInterrupt:
                break

        print("[system] closing server socket ...")
        self.server_socket.close()


    def receive_fixed_length_msg(self, sock, msglen):
        message = b''
        while len(message) < msglen:
            chunk = sock.recv(msglen - len(message))

            if chunk == b'':
                raise RuntimeError("socket connection broken")
            message = message + chunk

        return message


    def receive_message(self, sock):
        header = self.receive_fixed_length_msg(sock, self.HEADER_LENGTH)
        message_length = struct.unpack("!H", header)[0]

        message = None
        if message_length > 0:
            message = self.receive_fixed_length_msg(sock, message_length)
            message = message.decode("utf-8")

        return message


    def send_message(self, sock, message):
        encoded_message = json.dumps(message).encode("utf-8")

        header = struct.pack("!H", len(encoded_message))

        message = header + encoded_message
        sock.sendall(message)


    def send_message_to_all(self, c, message):
        for client in self.clients:
            if client != c:
                self.send_message(client, message)


    def getClient(self, id):
        for client in self.clients:
            if client.getpeername()[1] == id:
                return client
            

    def client_thread(self, client_sock, client_addr, user):
        print(f"[system] connected with {client_addr[0]}:{client_addr[1]}")
        print(f"[system] we now have {len(self.clients)} clients")
        self.connected_users[user] = client_addr[1]
        print('Established SSL connection with: ', user)

        try:
            while True:
                msg_received = self.receive_message(client_sock)

                if not msg_received:
                    break

                curr_date = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
                data = json.loads(msg_received)
                data["sender"] = user

                if "receiver" in data:
                    if data["receiver"] not in self.connected_users:
                        print(f"[Chat] [{curr_date}] {user} tried to send private message to non-existing user '{data['receiver']}'")
                        self.send_message(client_sock, {"sender": "System", "message": f"User '{data['receiver']}' do not exist"})
                    else:
                        data["private"] = True
                        receiver = self.getClient(self.connected_users[data["receiver"]])
                        print(f"[Chat] [{curr_date}] {user} send private message to {data['receiver']}: {data['message']}")
                        self.send_message(receiver, data)
                        self.send_message(client_sock, {"sender": "System", "message": f"Private message send to '{data['receiver']}'"})

                else:
                    print(f"[Chat] [{curr_date}] {user}: {data['message']}")
                    self.send_message_to_all(client_sock, data)
        except:
            pass

        with self.clients_lock:
            self.clients.remove(client_sock)

        del self.connected_users[user]
        print(f"User {user} left the chat")
        self.send_message_to_all(client_sock, {"sender": "System", "message": f"User {user} left the chat"})

        print(f"[system] we now have {len(self.clients)} clients")
        client_sock.close()


    def setup_SSL_context(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=DeprecationWarning)
            context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.verify_mode = ssl.CERT_REQUIRED
        context.load_cert_chain(certfile=self.serverCertFile, keyfile=self.serverKeyFile)
        context.load_verify_locations(self.clientsCert)
        context.set_ciphers(self.cipher)
        return context


if __name__ == "__main__":
    server = Server()


