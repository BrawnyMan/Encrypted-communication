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

At the start you will be prompted to choose user, which are avaliable (have certification). You will join the chat with that name. You can add new user names with command in terminal:
```bash
bash createUser.sh [username]
```
or
```bash
chmod +x createUser.sh
./createUser.sh [username]
```
When you add user, the user.key and user.crt will be added in clients/certs and clients/privateKeys forlder. In the server folder there is "clients.pem" file in which are all certifications of users that server will accept.

>Commands for client:
- `/msg [user] [message]` - messsage user privately
- `/exit` - leave the chat
