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
chmod +x crecreateUser.sh
./createUser.sh [username]
```

>Commands for client:
- `/msg [user] [message]` - messsage user privately
- `/exit` - leave the chat
