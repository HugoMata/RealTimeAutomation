import socket

HOST = 'localhost'  # Standard loopback interface address (localhost)
PORT = 40000        # Port to listen on (non-privileged ports are > 1023)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT)) #associating the socket with a specific network interface and port number
    s.listen() #enables a server to accept() connections. It makes it a “listening” socket
    print('Aguardando cliente...')
    conn, addr = s.accept()
    with conn:
        print('Connected by', addr)
        while True:
            data = conn.recv(1024)
            
            conn.sendall(data)