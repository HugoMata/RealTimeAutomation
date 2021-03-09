### Trabalho Prático ATR - Parte 3 - Hugo Melo da Mata - 2016090531 ###

import threading
import time
import math
import matplotlib.pyplot as plt
import pathlib
from tkinter import *
import socket

# Parâmetros globais
t_end = time.time() + 60 # horizonte de simulação
dt = 1 # variação do tempo
gamma1 = 0.4 # antes 0.2
gamma2 = 0.2 # antes 0.1

# Condições iniciais das variáveis globais:

QI1 = 2 # Vazão de entrada TQ1
QI2 = 1 # Vazão de entrada TQ2
QO1 = 0 # Vazão de saída TQ1
QO2 = 0 # Vazão de saída TQ2
h1 = 0 # Altura controla TQ1
h2 = 0 # Altura controla TQ2
h1_setpoint = 5 # Setpoint altura TQ1
h2_setpoint = 2.5 # Setpoint altura TQ2

# Declaração de Mutex

mutex_h1 = threading.Lock()
mutex_h2 = threading.Lock()
mutex_QI1 = threading.Lock()
mutex_QI2 = threading.Lock()
mutex_QO1 = threading.Lock()
mutex_QO2 = threading.Lock()
lock_list_h1 = threading.Lock()
lock_list_h2 = threading.Lock()
lock_list_QI1 = threading.Lock()
lock_list_QI2 = threading.Lock()

h1_Lista = []
h2_Lista = []
QI1_Lista = []
QI2_Lista = []

class thread(threading.Thread):
  def __init__(self, threadID, R, r, H, h_initial):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.R = R
      self.r = r
      self.H = H
      self.h_control = h_initial
      self.tempo = 0
      self.h1_control = 0
      self.h2_control = 0

  # inicializador da thread
  def run(self):
      global t_end
      global QI1
      global QI2
      global QO1
      global QO2
      global h1
      global h2
      global mutex_h1
      global mutex_h2
      global mutex_QO1
      global mutex_QO2
      global lock_list_h1
      global lock_list_h2
      global h1_Lista
      global h2_Lista

      print ("Starting process_thread_{}" .format(self.threadID))

      time.sleep(2)

      while time.time() < t_end:
          ### TQ1 ###
          if self.threadID == 1:
            with mutex_h1:
              self.h1_control = self.calc_integral_TQ()
              h1 = self.h1_control
              with lock_list_h1:
                h1_Lista.append(h1)
                h1_Lista.append(h1)
              with mutex_QO1:
                QO1 = gamma1 * math.sqrt(self.h1_control)

            print("Altura controlada TQ1: {:.3f}" .format(self.h1_control))
            print("Vazão TQ1: {:.3f}" .format(QO1))

          ### TQ2 ###
          elif  self.threadID == 2:
            with mutex_h2:
              self.h2_control = self.calc_integral_TQ()
              h2 = self.h2_control
              with lock_list_h2:
                h2_Lista.append(h2)
                h2_Lista.append(h2)
              with mutex_QO2:
                QO2 = gamma2 * math.sqrt(self.h2_control)

            print("Altura controlada TQ2: {:.3f}" .format(self.h2_control))
            print("Vazão TQ2: {:.3f}" .format(QO2))

          time.sleep(0.5)

      print ("Exiting process_thread_{}" .format(self.threadID))

  #calcula altura atual do tanque
  def calc_integral_TQ(self): #Runge-kutta
    dt = 1
    k1 = self.calc_diferencial_TQ(self.tempo, self.h_control) #tempo comeca em 0, integral em 0
    k2 = self.calc_diferencial_TQ(self.tempo+dt/2, self.h_control+dt*k1/2)
    k3 = self.calc_diferencial_TQ(self.tempo+dt/2, self.h_control+dt*k2/2)
    k4 = self.calc_diferencial_TQ(self.tempo+dt, self.h_control+dt*k3)
    # Combine partial steps.
    self.h_control += dt/6*(k1+2*k2+2*k3+k4)
    self.tempo += dt
    return(self.h_control)

  #calcula variação instantânea no tanque
  def calc_diferencial_TQ(self, tempo, h_control):
    # verificando altura controlada do TQ
    h_control = max(0,h_control)
    h_control = min(100,h_control)

    if self.threadID == 1:
      diferencial_TQ = (QI1 - QO1 - QI2)/(math.pi*(self.r+((self.R-self.r)/self.H)*self.h_control))**2
    elif self.threadID == 2:
      diferencial_TQ = (QI2 - QO2)/(math.pi*(self.r+((self.R-self.r)/self.H)*self.h_control))**2
    return  diferencial_TQ

class softPLC_thread(threading.Thread):
  def __init__(self):
      threading.Thread.__init__(self)
      
  # inicializador da thread
  def run(self):
      global t_end
      global QI1
      global QI2
      global mutex_QI1
      global mutex_QI2
      global lock_list_QI1
      global lock_list_QI2
      global QI1_Lista
      global QI2_Lista
      global h1_setpoint
      global h2_setpoint

      #Configurações servidor
      HOST = 'localhost'  # localhost
      PORT = 40000

      print ("Starting softPLC_thread")

      path = str(pathlib.Path(__file__).parent.absolute())

      while time.time() < t_end:

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
          s.bind((HOST, PORT)) #associating the socket with a specific network interface and port number
          s.listen() #enables a server to accept() connections. It makes it a “listening” socket
          print('Aguardando cliente...')
          conn, addr = s.accept()
          with conn:
              print('Connectado por:', addr)
              while True:

                if (h1 > 1.1*h1_setpoint):
                  with mutex_QI1:
                    QI1 -= 0.2
                    QI1 = max(0,QI1)
                    with lock_list_QI1:
                      QI1_Lista.append(QI1)
                elif (h1 < 0.9*h1_setpoint):
                  with mutex_QI1:
                    QI1 += 0.2
                    with lock_list_QI1:
                      QI1_Lista.append(QI1)

                print("Vazão entrada TQ1: {:.1f}" .format(QI1))
                
                if (h2 > h2_setpoint):
                  with mutex_QI2:
                    QI2 -= 0.1
                    QI2 = max(0,QI2)
                    with lock_list_QI2:
                      QI2_Lista.append(QI2)
                elif (h2 < h2_setpoint):
                  with mutex_QI2:
                    QI2 += 0.1
                    with lock_list_QI2:
                      QI2_Lista.append(QI2)

                print("Vazão entrada TQ2: {:.1f}" .format(QI2))

                message = ("Altura controlada TQ1: {:.1f} \n"
                "Altura controlada TQ2: {:.1f} \n"
                "Vazao entrada TQ1: {:.1f} \n"
                "Vazao entrada TQ2: {:.1f} \n"
                "Vazao saida TQ1: {:.1f} \n"
                "Vazao saida TQ2: {:.1f} \n" .format(h1, h2, QI1, QI2, QO1, QO2))

                conn.send(message.encode("ascii"))

                historiador = open(path + "/historiador.txt",'a')
                historiador.write(message)
                historiador.close()

                AlteracaoClient = s.recv(1024) # read the server’s reply and then prints it
                if AlteracaoClient[0] == 'TQ1':
                  h1_setpoint = float(AlteracaoClient[1])
                elif AlteracaoClient[0] == 'TQ2':
                  h2_setpoint = float(AlteracaoClient[1])
                
                time.sleep(0.25)

      print ("Exiting softPLC_thread")

class Logger_Thread(threading.Thread):
  #salvará periodicamente (a cada segundo) os valores de h1, h2, qi1 e qi2, além do time stamp.
  def __init__(self):
      threading.Thread.__init__(self)

  # inicializador da thread
  def run(self):
      print ("Starting logger_thread")

      path = str(pathlib.Path(__file__).parent.absolute())

      while time.time() < t_end:

        log = open(path + "/log.txt",'a')

        log.write("Time stamp: {:.3f}\n" .format(time.time() - start_time))

        if h1_Lista:
          log.write("Altura controlada TQ1: {:.3f}\n" .format(h1_Lista[-1]))
        if h2_Lista:
          log.write("Altura controlada TQ2: {:.3f}\n" .format(h2_Lista[-1]))
        if QI1_Lista:
          log.write("Vazão de entrada TQ1: {:.3f}\n" .format(QI1_Lista[-1]))
        if QI2_Lista:
          log.write("Vazão de entrada TQ2: {:.3f}\n" .format(QI2_Lista[-1]))

        log.close()

        time.sleep(1)

      print ("Exiting logger_thread")

class Interface_Thread(threading.Thread):
  def __init__(self):
      threading.Thread.__init__(self)

  # inicializador da thread
  def run(self):

      global h1_setpoint
      global h2_setpoint

      print ("Starting interface_thread")

      while time.time() < t_end:

        root = Tk()
        root.title('interface_thread')
        self.h1_setpoint_changed = StringVar()
        self.h2_setpoint_changed = StringVar()

        def Modificate():
          global h1_setpoint
          global h2_setpoint
          
          if self.h1_setpoint_changed != h1_setpoint and self.h1_setpoint_changed:
            with mutex_h1:
              h1_setpoint = float(self.h1_setpoint_changed.get())
          if self.h2_setpoint_changed != h2_setpoint and self.h2_setpoint_changed:
            with mutex_h2:
              h2_setpoint = float(self.h2_setpoint_changed.get())

        Label(root, text="Digite valor para h1_setpoint:").grid(row=0, sticky=W)  #label
        Entry(root, textvariable = self.h1_setpoint_changed).grid(row=0, column=1, sticky=E) #entry textbox

        Label(root, text="Digite valor para h2_setpoint:").grid(row=1, sticky=W)  #label
        Entry(root, textvariable = self.h2_setpoint_changed).grid(row=1, column=1, sticky=E) #entry textbox

        Button(root, text="Alterar valores", command=Modificate).grid(row=3, column=0, sticky=W) #button
        Button(root, text="Fechar e finalizar thread", command=root.quit).grid(row=3, column=1, sticky=W) #button
        
        root.mainloop()

      print ("Exiting interface_thread")

### mainThread ###

start_time = time.time()

### TQ1 ###
# QI1 = 2
# r1 = 4
# R1 = 8
# H1 = 10
# h1_initial = h1_setpoint = 5
process_thread_1 = thread(1, 8, 4, 10, 6) #threadID, R, r, H, h_initial

### TQ2 ###
# QI2 = 1
# r2 = 2
# R2 = 4
# H2 = 5
# h2_initial = h2_setpoint = 2,5
process_thread_2 = thread(2, 4, 2, 5, 1) #threadID, R, r, H, h_initial

softPLC = softPLC_thread()

logger_thread = Logger_Thread()

interface_thread = Interface_Thread()

# Starting Threads
process_thread_1.start()
process_thread_2.start()
softPLC.start()
logger_thread.start()
interface_thread.start()

#Joining Threads

process_thread_1.join()
process_thread_2.join()
softPLC.join()
logger_thread.join()
interface_thread.join()

# Plotando resultados

QI1_Lista_size = len(QI1_Lista)
h1_Lista_size = len(h1_Lista)

plt.subplot(2,1,1)
plt.plot(list(range(QI1_Lista_size)), QI1_Lista, 'b', label='Vazão entrada TQ1')
plt.plot(list(range(h1_Lista_size)), h1_Lista, 'r', label='Altura controlada TQ1')
plt.xlabel('Tempo')
plt.ylabel('Vazão')
plt.title('Tanque 1')
plt.legend(loc='best')

QI2_Lista_size = len(QI2_Lista)
h2_Lista_size = len(h2_Lista)

plt.subplot(2,1,2)
plt.plot(list(range(QI2_Lista_size)), QI2_Lista, 'b', label='Vazão entrada TQ2')
plt.plot(list(range(h2_Lista_size)), h2_Lista, 'r', label='Altura controlada TQ2')
plt.xlabel('Tempo')
plt.ylabel('Vazão')
plt.title('Tanque 2')
plt.legend(loc='best')

plt.show()

print("\nFim...")