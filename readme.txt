### Trabalho Prático ATR - Parte 1 - Hugo Melo da Mata - 2016090531 ###

Vocabulário:
TQ1: Tanque 1
TQ2: Tanque 2

Aplicáveis aos dois tanques:
R: raio maior
r: raio menor
H: altura do tanque
h: altura controlada
h_initial: altura controlada inicial
h_setpoint: setpoint desejado para o nível da água

------------------------------------------------------------------------------------------------------------------

Foram utilizadas as bibliotecas:

threading
time
math
matplotlib.pyplot
tkinter # Adicionada na parte 2 do trabalho para geração de User Form

------------------------------------------------------------------------------------------------------------------

Ao início do código é possível setar parâmetros globais e condições iniciais das variáveis globais dos tanques:

# Parâmetros globais
t_end = time.time() + 30 # horizonte de simulação, o 30 pode ser alterado para estender a simulação e o gráfico ao final
dt = 1 # variação do tempo
gamma1 = 0.4 # constante gamma 1
gamma2 = 0.2 # constante gamma 2

# Condições iniciais das variáveis globais dos tanques:

QI1 = 2 # Vazão de entrada TQ1
QI2 = 1 # Vazão de entrada TQ2
QO1 = 0 # Vazão de saída TQ1
QO2 = 0 # Vazão de saída TQ2
h1 = 0 # Altura controla TQ1
h2 = 0 # Altura controla TQ2

------------------------------------------------------------------------------------------------------------------

Para setar os parâmetros dos tanques basta ir até o início da mainThread e colocar os valores de entrada no
construtor da classe thread. Inicialmente estão alocados como:

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

------------------------------------------------------------------------------------------------------------------

O h1_setpoint e h2_setpoint diferente da primeira parte do trabalho, agora são variáveis globais declaradas no 
início do programa para que a thread interface_thread tenha permissão para alterar seus valores. Antes elas
estavam declaradas apenas no escopo da softPLC.

------------------------------------------------------------------------------------------------------------------

USER FORM interface_thread :

Para modificar os valores de h1_setpoint e h2_setpoint, basta inserir os números nos campos em branco, 
atentando para colocar " . " para casas decimais, exemplo: 8.75. Em seguida basta clicar em "Alterar valores"
e as variáveis, acompanhadas de mutex, serão alteradas.

