# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 08:52:47 2026

@author: Rivera
C22211720
proyecto
"""

from abc import ABC, abstractmethod
import json
import os
import random

class TamaYoshi(ABC):
    def __init__(self,nombre,genero,vida,sueno,felicidad,hambre):
        self.nombre=nombre
        self.genero=genero
        self.vida=vida
        self.sueno=sueno
        self.felicidad=felicidad
        self.hambre=hambre
        self.tiempo=0
        self.crecer=0
        self.vivo=True
        self.aviso= ""
        
    @abstractmethod
    def evolucionar(self):
        pass
    
    @abstractmethod
    def sonido(self):
        pass
    
    def datos(self):
        if self.genero == 0:
            gen = "Macho"       
        elif self.genero == 1:
            gen = "Hembra"
        print("\nInformación de tu Yoshi")
        print("-----------------------")
        print(f"Nombre: {self.nombre}\nColor: {self.color}\nGenero: {gen}\nEtapa: {self.etapa}")

    def estado(self):      
        print("\nEstado de tu Yoshi")
        print("-----------------------")
        print(f"Puntos de vida: {self.vida}\nNivel de felicidad: {self.felicidad}\nNivel de sueño: {self.sueno}\nNivel de hambre: {self.hambre}\n")
      
    def morir(self):
        self.vivo=False        
        
    def danar(self):   
        
        if self.hambre >= 80:
           self.vida -= 5
           
        if self.sueno >= 80:
           self.vida -= 2.5
           
        if self.felicidad == 20:
           self.vida -= 1
       
        if self.vida<=0:
           self.vida=0
           self.morir()

    def curar(self):
        if not self.vivo:
            return
        print("Curando a",self.nombre)
        self.vida+=20
        if self.vida>100:
            self.vida=100
        print("Puntos de vida:",self.vida,"\n")

    def comer(self,comida):
        if not self.vivo:
            return
        if self.hambre>=10:
            print(self.nombre," comió ",comida)
            if comida == "Manzana":
                self.hambre-=15
                if self.hambre<=0:
                    self.hambre=0
            elif comida == "Taco":
                self.hambre-=30
                if self.hambre<=0:
                    self.hambre=0   
            elif comida == "Hamburguesa":
                self.hambre-=35
                if self.hambre<=0:
                    self.hambre=0 
        else:
            print(f"{self.nombre} aún no quiere comer\n")
    
    def dormir(self):
        if not self.vivo:
            return
        print(self.nombre," está durmiendo")
        if self.sueno>=40:
            self.sueno-=50
            if self.sueno<0:
                self.sueno=0
            self.hambre+=20
            if self.hambre >= 100:
                self.hambre=100
        else:
            print(f"{self.nombre} aún no quiere dormir\n")
            
    def jugar(self):
        if not self.vivo:
            return
        print(self.nombre,"está jugando")
        self.felicidad+=15
        if self.felicidad>100:
            self.felicidad=100
        self.sonido()
        self.hambre+=10
        if self.hambre >= 100:
            self.hambre=100
        self.sueno+=15
        if self.sueno >= 100:
            self.sueno=100
        
    def pasar_tiempo(self):
        prob_hambre=0.2
        prob_sueno=0.25
        prob_felicidad=0.3
        prob_dano=0.5
        
        self.tiempo += 1
        if random.random() < prob_dano:    
            self.danar()
            
        if self.crecer == 20:
            self.evolucionar()      
            
        if self.hambre <= 20 and self.sueno <=10 and self.felicidad>=90:
            self.crecer += 1
            
        if random.random() < prob_hambre:    
            self.hambre += 2
            
        if random.random() < prob_sueno: 
            self.sueno += 1
            
        if random.random() < prob_felicidad: 
            self.felicidad -= 1
            
        if self.hambre >= 100:
            self.hambre=100
            
        if self.sueno >= 100:
            self.sueno=100
            
        if self.felicidad <= 0:
            self.felicidad=0
            
        if not self.vivo:
            return        
        
    def guardar(self, archivo="datos/yoshi.json"):
        if not self.vivo:
            print("No se puede guardar un Yoshi muerto.")
            return        
        carpeta = os.path.dirname(archivo)
        if carpeta:
            os.makedirs(carpeta, exist_ok=True)
        datos = {
            "nombre": self.nombre,
            "genero": self.genero,
            "vida": self.vida,
            "sueno": self.sueno,
            "felicidad": self.felicidad,
            "hambre": self.hambre,
            "tiempo": self.tiempo,
            "crecer": self.crecer,
            "color": self.color,
            "etapa": self.etapa,
        }
        with open(archivo, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=4, ensure_ascii=False)
        print("Estado guardado")