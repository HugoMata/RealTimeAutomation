import socket

HOST = 'localhost'  # The server's hostname or IP address 127.0.0.1
PORT = 40000        # The port used by the server

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT)) 
print("Conexão com o servidor estabelecida.")
while True:
    #s.sendall(b'Hello, world') #send a message
    data = s.recv(1024) # read the server’s reply and then prints it
    print('Recebido: ', (data))

    print("Digite no modelo TQ1-Number ou TQ2-Number")
    Alteracao = input()
    Alteracao = Alteracao.split("-",1)
    TQ = Alteracao[0]
    Setpoint = Alteracao[1]
    message = [TQ, Setpoint]
    s.send(message)
