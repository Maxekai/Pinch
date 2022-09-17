import numpy as np
import time
import copy

class Corr:
    corrientes=[]
    temperaturas=[]
    nombre=0
    def __init__(self,FCp,Tini,Tfin):
        assert Tini!=Tfin
        self.nombre=Corr.nombre
        if Tfin>Tini:
            self.cold=True
            self.Ti, self.Tf = Tini+DT ,Tfin+DT
        else:
            self.cold=False
            self.Ti, self.Tf = Tini, Tfin
            
        if self.cold:
            #Se utiliza el convenio de que las corrientes colds tienen FCp negativa
            self.FCp=-FCp
        else:
            self.FCp=FCp
        #los datos de las corrientes se guardan todas en una lista porque asi se crea el array facilmente    
        self.corrientes.append([self.nombre,self.FCp, self.Ti,self.Tf,self.Q])
        if self.Ti not in self.temperaturas:
            self.temperaturas.append(self.Ti)
        if self.Tf not in self.temperaturas:
            self.temperaturas.append(self.Tf)
            
        #Esto sirve para darle un numero a cada corriente. Cada vez que se crea una corriente, la clase recuerda cuantos ya existen
        #Por eso es un atributo de clase, no de la instancia
        Corr.nombre+=1       
    def __str__(self):
        return f'FCp: {self.FCp} Tini: {self.Ti} Tfinal: {self.Tf} Q: {self.Q}'
    
    def __repr__(self):
        return f'{self.nombre}'
    
    @classmethod
    @property
    def arr(self):
        #Metodo de clase porque crea el array de todas las corrientes
        return np.array(self.corrientes)
    
    @classmethod
    @property
    def corrs(self):
        return self.corrientes
        
    @property
    def RangoT(self):
        return self.Ti-self.Tf
    
    @property
    def Q(self,abs=False):
        if abs==False:
            return self.RangoT*self.FCp
        if abs==True:
            return abs(self.RangoT*self.FCp)
        
    @classmethod
    @property
    def temperatur(cls):
        return cls.temperaturas

    
class CreaInterv(Corr):
    #La clase hereda de Corr para poder utilizar el metodo de clase que devuelve todas las temperaturas
    @classmethod
    def Crea(self):
        #Se crean los intervalos de temperatura y se le asigna a cada intervalo las corrientes que les corresponde
        listatemps=copy.deepcopy(self.temperatur)
        listatemps.sort(reverse=True)
        listaobjetos=[]
        while len(listatemps)>1:
            corr_intervalo=[]
            inf=listatemps[0]
            sup=listatemps[1]
            for corriente in self.corrs:
                rango_temps=corriente[2:4]
                minimo, maximo =min(rango_temps), max(rango_temps)
                if minimo < sup and maximo > sup or minimo < inf and maximo > inf:
                    corr_intervalo.append(corriente)
            del listatemps[0]
            nombre= Intervalo(inf,sup,corr_intervalo)
            listaobjetos.append(nombre)
        return listaobjetos
    

class Intervalo:
    def __init__(self,tsup,tinf,members):
        self.tinf=tinf
        self.tsup=tsup
        self.members=members
        
    def __repr__(self):
        #Se utiliza a la hora de enseñar que hay en cada intervalo
        return f'\n{self.tinf}-{self.tsup} : Corrientes: {[i[0] for i in self.members]} FCp: {self.FCpGeneral} Q: {self.Q}'
    
    def __str__(self):
        return f'{self.tinf}-{self.tsup}'

    @property
    def FCpGeneral(self):
        return sum([i[1] for i in self.members]) 
    
    @property
    def Q(self):
        return self.FCpGeneral*(self.tsup-self.tinf)    

class ServCalculado:
    def __init__(self,intervalos):
        self.listaQ=[]
        self.q=0
        for intervalo in intervalos:
            #Se añaden los Q de los intervalos a una lista para realizar el algoritmo de resolucion de los servicios minimos
            self.q+=intervalo.Q
            self.listaQ.append(self.q)
            
    def __repr__(self):
        return f'{self.listaQ}'    
    
    
    def calcularServCal(self):
        #Se realiza el algoritmo de resolucion del pinch
        qminima=min(self.listaQ)
        #Se sabe que los servicios calidos necesarios es la -q minima de los intervalos, si esta es positiva no hay servicios cálidos.
        if qminima>0:   
            qminima=0
        return -qminima
    
    def calcularServFriosyPinch(self,servical):
        #El Calculo de los servicios frios y el pinch se hace a partir del mismo proceso, por eso se calculan juntos
        nueva_lista_q=[servical+q for q in self.listaQ] 
        #Esto sirve para encontrar la T donde la Q es 0, es decir el pinch.
        Tpinch= self.EncontrarT(nueva_lista_q,Corr.temperaturas)
        servifrio=nueva_lista_q[-1]
        return Tpinch,servifrio
    
    def Aplicar(self):
        servical=self.calcularServCal()
        Tpinch,servifrio=self.calcularServFriosyPinch(servical)
        self.resultados= f'Servicios calidos {servical} kW, Servicios frios: {servifrio} kW, Temp. Pinch: {Tpinch} C'
        return servical, servifrio,Tpinch
    
    def EncontrarT(self,listaq,listat):
        listat.sort()
        indice=listaq.index(0.0)
        return listat[indice]
    
    @property
    def servicios(self):
        return self.resultados


    
def setDT():
    print("Introduce el valor de DT (Margen de temperatura para los intercambiadores de calor)")
    return float(input())

def separarInput(datos):
    separados=datos.split(",")
    return [float(elemento) for elemento in separados]

def crearCorrs():
    corrs=[]
    while True:
        print(f"Introduce los datos de la corriente numero {len(corrs)+1} \n Formato: FCp,TempInicial,TempFinal")
        print(f"Introduzca 0 para terminar la creación de corrientes")
        datos=input()
        if datos!= "0":
            datosSeparados=separarInput(datos)
            corrs.append(Corr(datosSeparados[0],datosSeparados[1],datosSeparados[2]))
        else:
            return corrs
        
if __name__ == "__main__":
    #Crea el margen de temperaturas y las corrientes, muestra el array de corrientes
    DT=setDT()
    ListaCorrientes= crearCorrs()
    print(Corr.arr)
    #Crea la lista de intervalos y una copia profunda de ella para evitar que se modifique la original
    ListaInterv=CreaInterv.Crea()
    ListaIntervalosCopia=copy.deepcopy(ListaInterv)
    print(ListaInterv)
    #Se calculan los servicios y a partir de ahí se calculan los fríos y el pinch
    ServCalc=(ServCalculado(ListaInterv))
    ServCalc.Aplicar()
    print(ServCalc.servicios)



