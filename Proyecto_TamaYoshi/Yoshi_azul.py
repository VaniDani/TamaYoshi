# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 08:54:03 2026

@author: Rivera
C22211720
proyecto
"""

from Yoshi import Yoshi

class YoshiAzul(Yoshi):
    def volar(self):
        print("Se puso a volar")
        self.felicidad += 10
        if self.felicidad >= 100:
            self.felicidad=100
            
        self.sueno+=10
        if self.sueno >= 100:
            self.sueno=100

    def habilidad(self):
        self.volar()