# -*- coding: utf-8 -*-
"""
Created on Mon Nov  2 07:02:07 2026

@author: Rivera
C22211720
proyecto
"""
import json
import os

from Yoshi_verde import YoshiVerde
from Yoshi_rojo import YoshiRojo
from Yoshi_azul import YoshiAzul

ARCHIVO = "datos/yoshi.json"
CLASES = {"Verde": YoshiVerde, "Rojo": YoshiRojo, "Azul": YoshiAzul}


def cargar(archivo=ARCHIVO):
    if not os.path.exists(archivo):
        return None
    try:
        with open(archivo, "r", encoding="utf-8") as f:
            d = json.load(f)
        y = CLASES[d["color"]](d["nombre"], d["genero"], d["vida"],
                               d["sueno"], d["felicidad"], d["hambre"],
                               d["color"])
        y.tiempo = d["tiempo"]
        y.crecer = d["crecer"]
        y.etapa = d["etapa"]
        return y
    except (json.JSONDecodeError, KeyError):
        print("El archivo de guardado está dañado. Se creará un Yoshi nuevo.")
        return None


def borrar_partida(archivo=ARCHIVO):
    """Elimina el archivo de guardado si existe."""
    if os.path.exists(archivo):
        os.remove(archivo)
        print("Se borró la partida guardada.")


def main():
    """Abre la interfaz gráfica."""
    import interfaz      # aquí adentro para evitar un import circular
    interfaz.iniciar()


if __name__ == "__main__":
    main()