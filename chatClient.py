import ssl
import socket
import struct
import sys
import threading

import warnings
import os
import json


class Client:
    def __init__(self, host="localhost", port=1235):
        self.PORT = port
        self.HOST = host
        self.HEADER_LENGTH = 2
        self.cipher = "ECDHE-RSA-AES128-GCM-SHA256"
        self.exit = False

        self.name = self.getName()
        self.clientCertFile = f"clients/certs/{self.name}.crt"
        self.clientKeyFile = f"clients/privateKeys/{self.name}.key"
        self.serverCert = "server/server.crt"

        print("[system] connecting to chat server ...")
        self.my_ssl_ctx = self.setup_SSL_context()
        self.sock = self.my_ssl_ctx.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
        self.sock.connect((self.HOST, self.PORT))
        print("[system] connected!")

        self.run()


    def getName(self):
        names = {str(i): file[:-4] for i, file in enumerate(os.listdir("./clients/certs"))}
        
        for i in names:
            print(i + ": " + names[i])
        
        while True:
            index = input("Enter a number: ").strip()

            if not index.isdigit() or index not in names:
                print("Choose number for the name!!!")
                continue            
            break

        return names[index]


    def run(self):
        thread = threading.Thread(target=self.message_receiver)
        thread.daemon = True
        thread.start()

        print(f"Joined as user '{self.name}'")

        while not self.exit:
            try:
                msg_send = input("")
                data = {"message": msg_send}

                if msg_send == "/exit":
                    print("Leaving...")
                    break

                if msg_send.startswith("/msg"):
                    _, data["receiver"], data["message"] = msg_send.split(" ", 2)

                self.send_message(data)
            except KeyboardInterrupt:
                self.exit = True
                print("Exiting...")
            except ValueError:
                print("Wrong input. Try again")


    def receive_fixed_length_msg(self, msglen):
        message = b''
        while len(message) < msglen:
            chunk = self.sock.recv(msglen - len(message))

            if chunk == b'':
                raise RuntimeError("socket connection broken")
            message = message + chunk
        return message


    def receive_message(self):
        header = self.receive_fixed_length_msg(self.HEADER_LENGTH)
        message_length = struct.unpack("!H", header)[0]

        message = None
        if message_length > 0:
            message = self.receive_fixed_length_msg(message_length)
            message = message.decode("utf-8")

        return message


    def send_message(self, message):
        encoded_message = json.dumps(message).encode("utf-8")
        header = struct.pack("!H", len(encoded_message))
        message = header + encoded_message
        self.sock.sendall(message)


    def message_receiver(self):
        while not self.exit:
            msg_received = self.receive_message()
            
            if len(msg_received) > 0:
                data = json.loads(msg_received)

                if data["sender"] == "System":
                    print("[System] " + data["message"])

                    if data["message"].startswith("FAILED"):
                        self.exit = True
                        print("Exiting...")
                elif "private" in data:
                    print(f"[Chat] Private message from {data['sender']}: {data['message']}")
                else:
                    print(f"[Chat] {data['sender']}: {data['message']}")


    def setup_SSL_context(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=DeprecationWarning)
            context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.verify_mode = ssl.CERT_REQUIRED
        context.load_cert_chain(certfile=self.clientCertFile, keyfile=self.clientKeyFile)
        context.load_verify_locations(self.serverCert)
        context.set_ciphers(self.cipher)
        return context


if __name__ == "__main__":
    client = Client()