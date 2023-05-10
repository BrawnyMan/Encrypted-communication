# Encrypted-communication

1. Run server

```bash
python chatServer.py
```

2. Run client/s

```bash
python chatClient.py
```

> At the start

At the start, you will be prompted to choose between users who are available (have certification). You will join the chat with that name. You can add new user names with the following command in the terminal:
```bash
bash createUser.sh [username]
```
or
```bash
chmod +x createUser.sh
./createUser.sh [username]
```
When you add a user, the user.key and user.crt will be added to the clients/certs and clients/privateKeys folders. In the server folder, there is a "clients.pem" file, in which are all the certifications of users that the server will accept.

> Commands for the client:
- `/msg [user] [message]` - message the user privately
- `/exit` - leave the chat
