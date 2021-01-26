### Trabalho Prático ATR - Parte 1 - Hugo Melo da Mata - 2016090531 ###

import threading
import time
import math
import matplotlib.pyplot as plt

# Parâmetros globais
t_end = time.time() + 30 # hrizonte de simulação
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
      self.h1_setpoint = 5
      self.h2_setpoint = 2.5

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

      print ("Starting softPLC_thread")
      
      while time.time() < t_end:

        if (h1 > 1.1*self.h1_setpoint):
          with mutex_QI1:
            QI1 -= 0.2
            QI1 = max(0,QI1)
            with lock_list_QI1:
              QI1_Lista.append(QI1)
        elif (h1 < 0.9*self.h1_setpoint):
          with mutex_QI1:
            QI1 += 0.2
            with lock_list_QI1:
              QI1_Lista.append(QI1)

        print("Vazão entrada TQ1: {:.1f}" .format(QI1))

        if (h2 > self.h2_setpoint):
          with mutex_QI2:
            QI2 -= 0.1
            QI2 = max(0,QI2)
            with lock_list_QI2:
              QI2_Lista.append(QI2)
        elif (h2 < self.h2_setpoint):
          with mutex_QI2:
            QI2 += 0.1
            with lock_list_QI2:
              QI2_Lista.append(QI2)

        print("Vazão entrada TQ2: {:.1f}" .format(QI2))
        
        time.sleep(0.25)
    
      print ("Exiting softPLC_thread")

### mainThread ###

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

# Starting Threads
process_thread_1.start()
process_thread_2.start()
softPLC.start()

#Joining Threads

process_thread_1.join()
process_thread_2.join()
softPLC.join()

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