import math
import random
import numpy as np

class Recorrido:

    def __init__(self, N):
        self.puntaje = 0
        self.recorrido = np.zeros(N, dtype=int)

class TSPTW:

    def __init__(self):
        # Inicializacion de Variables
        self.ITERACIONES = 1000
        self.VALORMAXIMO = 10000000.0
        self.N = 0
        self.NIVEL = 2
        self.dist = None
        self.der = None
        self.izq = None
        self.movimientos = []
        self.valor = []
        self.local = []

        self.expansiones = 0
        self.politica = []
        self.visitado = []
        self.recorrido = []
        self.tamano_recorrido = 0
        self.aleatoreo = 0
    
    def calcularTSPTW(self, archivo_problema, tiempo_maximo):
        try:
            # Lectura de Archivo Problema
            with open(archivo_problema, 'r') as reader:
                # Captura de numero de filas y columnas 
                self.N = int(reader.readline())
                matriz_distancias = ""
                lista_intervalos = []

                for i in range (0, self.N):
                    matriz_distancias = matriz_distancias + reader.readline()
                
                for i in range (0, self.N):
                    linea_intervalos = reader.readline()
                    linea_intervalos = linea_intervalos.split(" ")
                    for g in linea_intervalos:
                        if (g != "") & (g != "\n"):
                            lista_intervalos.append(g)


            # Captura de matriz de distancias 
            matriz_distancias = matriz_distancias.replace("\n", " ")
            valor_matriz = np.array(matriz_distancias.split(" "))
            valor_matriz = np.delete(valor_matriz, valor_matriz.shape[0] - 1)

            print(f"N: {self.N}")

            #Convierte Matriz en numeros
            valor_matriz_float = valor_matriz.astype(np.float)
            self.dist = np.array(valor_matriz_float).reshape(self.N, self.N)

            print(self.dist)

            # Captura de intervalos de ventanas de tiempo
            intervalos_der = []
            intervalos_izq = []
            for i in range(0, len(lista_intervalos)):
                if i % 2 == 0:
                    intervalos_izq.append(lista_intervalos[i])
                else :
                    intervalos_der.append(lista_intervalos[i])

            intervalos_izq_np = np.array(intervalos_izq)
            intervalos_der_np = np.array(intervalos_der)

            self.izq = intervalos_izq_np.astype(np.float)
            self.der = intervalos_der_np.astype(np.float)

            print(self.izq)
            print(self.der)

            
            self.recorrido = np.zeros(self.N+2, dtype=int)

            self.tamano_recorrido = 0
            self.politica =  np.zeros([self.N, self.N])
            self.local = np.zeros([self.N, self.N, self.N])
            self.movimientos = np.zeros(self.N, dtype=int)
            self.valor = np.zeros(self.N)

            for i in range(0, self.N):
                self.visitado.append(False)
            
        except Exception as e:
            print("Error: {}".format(e))
    
    def movimientos_legales(self):
        previo = 0
        indice = 0
        distancia = 0.0
        costo = 0.0
        for i in range(1, self.tamano_recorrido):
            nodo = self.recorrido[i]
            costo += self.dist[previo][nodo]
            distancia = max(distancia + self.dist[previo][nodo], self.izq[nodo])
            previo = nodo
        
        if self.tamano_recorrido > 0:
            previo = self.recorrido[self.tamano_recorrido - 1]

        for i in range(1, self.N):
            if not self.visitado[i]:
                self.movimientos[indice] = i
                tardio = False
                for j in range(1, self.N):
                    if (j != i) & (not self.visitado[j]):
                        if ((distancia <= self.der[j]) 
                        & (distancia + self.dist[previo][j] <= self.der[j]) 
                        & (max(distancia + self.dist[previo][i], self.izq[i]) > self.der[j])):
                            tardio = True
                            break
                        
                if not tardio:
                    indice = indice + 1
        
        if indice == 0:
            for i in range(1, self.N):
                if not self.visitado[i]:
                    indice = indice + 1
                    self.movimientos[indice] = i
        
        return indice

    def lanzamiento(self):
        nodo = 0
        self.tamano_recorrido = 1
        for i in range(1, self.N):
            self.visitado[i] = False
        
        while self.tamano_recorrido < self.N:
            sucesores = self.movimientos_legales()
            for i in range(0, sucesores):
                self.valor[i] = math.exp(self.politica[nodo][self.movimientos[i]])
            suma = self.valor[0]
            for i in range(1, sucesores):
                suma += self.valor[i]
            valor_rand = random.uniform(0, 1) * suma
            i = 0
            suma = self.valor[0]
            while suma < valor_rand:
                i = i + 1
                suma += self.valor[i]
            
            self.tamano_recorrido = self.tamano_recorrido + 1
            self.recorrido[self.tamano_recorrido] = self.movimientos[i]
            self.visitado[self.movimientos[i]] = True
            nodo = self.movimientos[i]

        self.tamano_recorrido = self.tamano_recorrido + 1
        self.recorrido[self.tamano_recorrido] = 0
    
    def evaluar(self):
        distancia = 0.0
        costo = 0.0
        previo = 0
        violaciones = 0
        for i in range(1, self.N):
            nodo = self.recorrido[i]
            costo += self.dist[previo][nodo]
            distancia = max(distancia + self.dist[previo][nodo], self.izq[nodo])
            if distancia > self.der[nodo]:
                violaciones = violaciones + 1
            previo = nodo
        costo += self.dist[previo][0]
        distancia = max(distancia + self.dist[previo][0], self.izq[0])
        if distancia > self.der[0]:
            violaciones = violaciones + 1
        
        return 100000.0 * violaciones + costo
    
    def adaptar(self, viaje_r, nivel):
        for k in range(1, self.N):
            self.visitado[k] = False
        nodo = 0
        for ply in range(0, self.N):
            sucesores = 0
            for i in range(1, self.N):
                if not self.visitado[i]:
                    self.movimientos[sucesores] = i
                    sucesores = sucesores + 1
            self.local[nivel][nodo][self.recorrido[ply]] += 1.0
            z = 0.0
            for i in range(0, sucesores):
                z += math.exp(self.politica[nodo][self.movimientos[i]])
            for i in range(0, sucesores):
                self.local[nivel][self.movimientos[i]] -= (math.exp(self.politica[nodo][self.movimientos[i]]) / z)
            nodo = self.recorrido[ply]
            self.visitado[nodo] = True
    

    def busqueda(self, nivel):
        mejorRecorrido = Recorrido(self.N+1)
        mejorRecorrido.puntaje = self.VALORMAXIMO
        if nivel == 0:
            self.lanzamiento()
            mejorRecorrido.puntaje = self.evaluar()
            for j in range(0, self.N+1):
                mejorRecorrido.recorrido[j] = self.recorrido[j]
        else:
            for k in range(0, self.N):
                for n in range(0, self.N):
                    self.local[nivel][k][n] = self.politica[k][n]
            
            for i in range(0, self.ITERACIONES):
                viaje = Recorrido(self.N + 1)
                viaje = self.busqueda(nivel-1)
                puntaje_v = viaje.puntaje
                if puntaje_v < mejorRecorrido.puntaje :
                    mejorRecorrido.puntaje = puntaje_v
                    for j in range(0, self.N):
                        mejorRecorrido.recorrido[j] = viaje.recorrido[j]
                    if nivel > 2:
                        print("Nivel: {0}, Puntaje: {1}".format(nivel, puntaje_v))
                    self.adaptar(mejorRecorrido.recorrido, nivel)

            for k in range(0, self.N):
                for n in range(0, self.N):
                    self.politica[k][n] = self.local[nivel][k][n]
        
        return mejorRecorrido

tsptw = TSPTW()
tsptw.calcularTSPTW('problemas/SolomonPotvinBengio/rc_201.1.txt', 20)
resultado = tsptw.busqueda(2)
print("Mejor Puntaje: {}".format(resultado.puntaje))
print("Recorrido: {}".format(resultado.recorrido))
