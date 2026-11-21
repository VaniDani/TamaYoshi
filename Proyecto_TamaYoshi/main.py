# -*- coding: utf-8 -*-
"""
Created on Mon Nov  2 07:02:07 2026

@author: Rivera
C22211720
proyecto
"""
import json
import os
import threading
import random

from Yoshi_verde import YoshiVerde
from Yoshi_rojo import YoshiRojo
from Yoshi_azul import YoshiAzul

INTERVALO = 1
lock = threading.Lock()
PROB_SONIDO = 0.3
PROB_GENERO=0.5
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
    
def crear_nuevo():
    while True:
        color = input("Escoja el color de su Yoshi (Verde, Rojo, Azul): ").capitalize()
        if color in CLASES:
            break
        print("Color inválido")

    nombre = input("Nombre de su Yoshi: ").capitalize()
    
    if random.random() < PROB_GENERO:
        genero = 0
    else: 
        genero = 1
    print("Tu huevo de Yoshi esta creciendo!!")
    return CLASES[color](nombre, genero, 100, 0, 100, 20, color)

def mostrar_menu():
    print("\n===== MENÚ =====")
    print("1. Comer")
    print("2. Jugar")
    print("3. Dormir")
    print("4. Curar")
    print("5. Ver datos")
    print("6. Usar habilidad")
    print("7. Guardar")
    print("8. Salir")

def borrar_partida(archivo=ARCHIVO):
    """Elimina el archivo de guardado si existe."""
    if os.path.exists(archivo):
        os.remove(archivo)
        print("Se borró la partida guardada.")

def main():
    yoshi = cargar()
    if yoshi is None:
        print("No hay partida guardada. Vamos a crear un Yoshi nuevo.\n")
        yoshi = crear_nuevo()
    else:
        print(f"Partida cargada: {yoshi.nombre} ({yoshi.color})")

    yoshi.datos()

    detener = threading.Event()
    hilo = threading.Thread(target=tiempo_automatico, args=(yoshi, detener), daemon=True)
    hilo.start()

    while True:
        with lock:
            if yoshi.aviso:
                print("\n*", yoshi.aviso)
                yoshi.aviso = ""
            if not yoshi.vivo:
                print(f"{yoshi.nombre} murió. Fin del juego.")
                detener.set()
                borrar_partida()
                break                
        yoshi.estado()
        mostrar_menu()
        opcion = input("Elige una opción: ")

        with lock:
            if opcion == "1":
                if not yoshi.vivo:
                    continue
                c=0
                while c==0:
                    comida = input("\n¿Qué le quieres dar de comer? (M=Manzana, H=Hamburguesa, T=Taco): ").capitalize()
                    if comida == "T":
                        comida="Taco"
                        c=1
                    elif comida == "M":
                        comida="Manzana"
                        c=1
                    elif comida == "H":
                        comida="Hamburguesa"
                        c=1
                    else: 
                        print("Comida invalida")
                yoshi.comer(comida)
            elif opcion == "2":
                yoshi.jugar()
            elif opcion == "3":
                yoshi.dormir()
            elif opcion == "4":
                yoshi.curar()
            elif opcion == "5":
                yoshi.datos()
            elif opcion == "6":
                yoshi.habilidad()
            elif opcion == "7":
                yoshi.guardar(ARCHIVO)
            elif opcion == "8":
                if input("¿Guardar antes de salir? (s/n): ").strip().lower() == "s":
                    yoshi.guardar(ARCHIVO)
                print("¡Hasta luego!")
                detener.set()
                break
            else:
                print("Opción inválida")
                continue
            if random.random() < PROB_SONIDO:
                yoshi.sonido()

def tiempo_automatico(yoshi, detener):
    while not detener.wait(INTERVALO):
        with lock:
            yoshi.pasar_tiempo()

if __name__ == "__main__":
    main()