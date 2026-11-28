# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 08:53:37 2026

@author: Rivera
C22211720
proyecto
"""

from Yoshi import Yoshi

class YoshiVerde(Yoshi):
    def salto(self):
        print("Salto muy alto")
        self.felicidad += 10
        if self.felicidad >= 100:
            self.felicidad=100
            
        self.sueno+=10
        if self.sueno >= 100:
            self.sueno=100

    def habilidad(self):
        self.salto()