import socket

hostname = socket.gethostname()

print(hostname)

print(socket.gethostbyname(hostname))