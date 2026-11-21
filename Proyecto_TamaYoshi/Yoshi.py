# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 08:53:25 2026

@author: Rivera
C22211720
proyecto
"""

from TamaYoshi import TamaYoshi

class Yoshi(TamaYoshi):
    def __init__(self, nombre,genero,vida,sueno,felicidad,hambre,color):
        super().__init__(nombre,genero,vida,sueno,felicidad,hambre)
        self.color=color
        self.etapa="Bebé"
        
    def evolucionar(self):
        if self.crecer == 20:
            if self.etapa != "Adulto" :
                self.etapa = "Adulto"         
                self.aviso= f"{self.nombre} ahora es {self.etapa}"
        
    def sonido(self):
        print("Yoshiiiii!")