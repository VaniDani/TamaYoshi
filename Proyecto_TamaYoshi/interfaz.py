# -*- coding: utf-8 -*-
"""
Created on Sun Nov 22 20:25:46 2026

@author: Rivera
C22211720
proyecto
"""

import tkinter as tk
import os
import io
import random
from contextlib import redirect_stdout
from tkinter import messagebox

# La lógica compartida (guardado y clases de Yoshi) vive en main.py
from main import ARCHIVO, CLASES, cargar, borrar_partida

try:
    BASE = os.path.dirname(os.path.abspath(__file__))
except NameError:                      # por si se ejecuta sin __file__
    BASE = os.getcwd()
CARPETA_IMG = os.path.join(BASE, "imagenes")
CARPETA_SONIDO = os.path.join(BASE, "sonidos")
NOMBRE_SONIDO = "yoshi"       # busca sonidos/yoshi.wav, .ogg o .mp3

INTERVALO = 1000          # ms entre cada tick
PROB_GENERO = 0.5
PROB_SONIDO = 0.3         # probabilidad de que suene al terminar una acción
TIEMPO_GLOBO = 1500       # ms que se muestra el texto del sonido
TIEMPO_ECLOSION = 2500    # ms que tarda en abrirse el huevo
TIEMPO_ACCION = 2000      # ms que se muestra el cuadro de acción
TIEMPO_DORMIR = 5000      # ms que dura el sueño (fondo de noche)

MOSTRAR_CRECIMIENTO = True   # False quita la barra de crecimiento
META_CRECIMIENTO = 50        # se usa si Yoshi no define META_CRECER

ANCHO, ALTO = 800, 500
POS_YOSHI = (400, 380)       # centro-abajo del Yoshi en pantalla

COLOR_CAJA = "#ffe08a"
COLOR_TEXTO = "#a86a00"
COLOR_VIDA = "#c62828"
COLOR_FELIZ = "#f57c1f"
COLOR_SUENO = "#5c6bc0"
COLOR_HAMBRE = "#e0a800"
COLOR_CRECER = "#8e44ad"


class AppYoshi:
    def __init__(self, root):
        self.root = root
        self.yoshi = None
        self.juego_terminado = False
        self.color_elegido = None
        self.en_juego = False
        self.after_accion = None
        self.durmiendo = False
        self.usando_habilidad = False
        self.cache = {}            # imágenes ya cargadas (también evita que
                                   # Python las borre de memoria)

        self.canvas = tk.Canvas(root, width=ANCHO, height=ALTO,
                                highlightthickness=0)
        self.canvas.pack()

        yoshi = cargar()
        if yoshi is None:
            self.pantalla_elegir_huevo()
        else:
            self.yoshi = yoshi
            self.pantalla_juego()

    def cargar_imagen(self, nombre):
        if nombre not in self.cache:
            ruta = os.path.join(CARPETA_IMG, nombre + ".png")
            try:
                self.cache[nombre] = tk.PhotoImage(file=ruta)
            except tk.TclError:
                self.cache[nombre] = None
        return self.cache[nombre]

    def poner_imagen(self, nombre, x, y, anchor="center", tags=(),
                     state="normal"):
        imagen = self.cargar_imagen(nombre)
        if imagen is None:
            return None
        return self.canvas.create_image(x, y, image=imagen, anchor=anchor,
                                        tags=tags, state=state)

    def crear_boton(self, texto, imagen, comando, ancho_texto=8):
        """Botón con imagen si existe, o con texto si no.
        Devuelve (boton, ancho, alto) para poder acomodarlo."""
        img = self.cargar_imagen(imagen)
        if img:
            b = tk.Button(self.root, image=img, command=comando,
                          bd=0, relief="flat", highlightthickness=0,
                          bg=COLOR_CAJA, activebackground=COLOR_CAJA,
                          cursor="hand2")
            return b, img.width(), img.height()
        b = tk.Button(self.root, text=texto, width=ancho_texto,
                      command=comando)
        return b, 75, 32

    def limpiar(self):
        self.canvas.delete("all")

    def fondo(self, nombre="fondo_dia"):
        return self.poner_imagen(nombre, 0, 0, anchor="nw")

    def cambiar_fondo(self, nombre):
        self.canvas.delete(self.fondo_id)
        self.fondo_id = self.fondo(nombre)
        self.canvas.tag_lower(self.fondo_id)

    def cuadro_texto(self, texto):
        self.poner_imagen("cuadro_accion", 10, 435, anchor="nw")
        self.canvas.create_text(170, 462, text=texto,
                                font=("Arial", 16, "bold"), fill=COLOR_TEXTO)

    def dibujar_huevo(self, x, y, color, tag=""):
        return self.poner_imagen(f"huevo_{color.lower()}", x, y, tags=tag)

    def pantalla_elegir_huevo(self):
        self.limpiar()
        self.fondo()
        self.canvas.create_text(ANCHO // 2, 60, text="Elige tu huevo",
                                font=("Arial", 26, "bold"), fill="#2e7d32")
        posiciones = {"Verde": 200, "Rojo": 400, "Azul": 600}
        for color, x in posiciones.items():
            tag = f"huevo_{color}"
            self.dibujar_huevo(x, 250, color, tag)
            self.canvas.create_text(x, 345, text=color,
                                    font=("Arial", 14, "bold"), tags=tag)
            self.canvas.tag_bind(tag, "<Button-1>",
                                 lambda e, c=color: self.elegir_color(c))

    def elegir_color(self, color):
        self.color_elegido = color
        self.pantalla_nombre()

    def pantalla_nombre(self):
        self.limpiar()
        self.fondo()
        self.dibujar_huevo(ANCHO // 2, 180, self.color_elegido)
        self.canvas.create_text(ANCHO // 2, 290, text="¿Cómo se llamará?",
                                font=("Arial", 18, "bold"), fill="#2e7d32")

        # validate="key": revisa cada tecla (y lo que se pegue) y rechaza números
        self.entrada = tk.Entry(
            self.root, font=("Arial", 14), justify="center", validate="key",
            validatecommand=(self.root.register(self.nombre_valido), "%P"),
            invalidcommand=self.root.bell)
        self.canvas.create_window(ANCHO // 2, 330, window=self.entrada, width=220)
        self.entrada.focus_set()

        boton = tk.Button(self.root, text="Aceptar", width=10,
                          command=self.aceptar_nombre)
        self.canvas.create_window(ANCHO // 2, 380, window=boton)
        self.root.bind("<Return>", lambda e: self.aceptar_nombre())

    def nombre_valido(self, texto):
        return not any(c.isdigit() for c in texto)

    def aceptar_nombre(self):
        nombre = self.entrada.get().strip().capitalize()
        if not nombre:
            messagebox.showwarning("Nombre", "Escribe un nombre para tu Yoshi.")
            return
        self.root.unbind("<Return>")
        genero = 0 if random.random() < PROB_GENERO else 1
        self.yoshi = CLASES[self.color_elegido](nombre, genero, 100, 0, 100,
                                                20, self.color_elegido)
        self.animacion_eclosion()

    def animacion_eclosion(self):
        self.limpiar()
        self.fondo()
        self.dibujar_huevo(ANCHO // 2, 250, self.color_elegido)
        self.cuadro_texto("Creciendo...")
        self.root.after(TIEMPO_ECLOSION, self.pantalla_juego)

    def pantalla_juego(self):
        self.en_juego = True
        self.limpiar()
        self.fondo_id = self.fondo("fondo_dia")
        self.dibujar_yoshi()
        self.dibujar_panel()
        self.crear_botones()
        self.crear_cuadro_accion()
        self.crear_cuadro_datos()
        self.actualizar_pantalla()
        self.root.after(INTERVALO, self.tick)

    def dibujar_yoshi(self):
        color_nombre = self.yoshi.color.lower()
        etapa = "adulto" if self.yoshi.etapa == "Adulto" else "bebe"
        if not self.yoshi.vivo or self.durmiendo:
            # Muerto y dormido usan la misma imagen
            nombre = f"yoshi_{color_nombre}_{etapa}_dormido"
        elif self.usando_habilidad:
            nombre = f"yoshi_{color_nombre}_habilidad"
        else:
            nombre = f"yoshi_{color_nombre}_{etapa}"

        x, y = POS_YOSHI
        self.poner_imagen(nombre, x, y, anchor="s", tags="yoshi_dibujo")
        # El Yoshi queda justo encima del fondo y debajo de lo demás
        self.canvas.tag_raise("yoshi_dibujo", self.fondo_id)
        self.etapa_dibujada = self.yoshi.etapa

    def dibujar_panel(self):
        self.poner_imagen("cuadro_barras", 10, 10, anchor="nw")

        configuracion = [("vida", COLOR_VIDA, 25), ("felicidad", COLOR_FELIZ, 55),
                         ("sueno", COLOR_SUENO, 85), ("hambre", COLOR_HAMBRE, 115)]
        self.barras = {}
        for atributo, color, y in configuracion:
            self.canvas.create_rectangle(50, y, 185, y + 16,
                                         fill="white", outline="")
            self.barras[atributo] = self.canvas.create_rectangle(
                50, y, 185, y + 16, fill=color, outline="")
            self.poner_imagen(f"icono_{atributo}", 30, y + 8)

        if MOSTRAR_CRECIMIENTO:
            self.canvas.create_rectangle(50, 145, 185, 161, fill="white",
                                         outline="", tags="barra_crecer")
            self.barra_crecer = self.canvas.create_rectangle(
                50, 145, 185, 161, fill=COLOR_CRECER, outline="",
                tags="barra_crecer")
            self.poner_imagen("icono_crecer", 30, 153, tags="barra_crecer")

    def crear_cuadro_datos(self):
        self.poner_imagen("cuadro_datos", 570, 10, anchor="nw")
        self.texto_datos = self.canvas.create_text(
            680, 57, text="", width=200, justify="center",
            font=("Arial", 13, "bold"), fill=COLOR_TEXTO)

    def crear_cuadro_accion(self):
        self.poner_imagen("cuadro_accion", 10, 435, anchor="nw",
                          tags="caja_accion", state="hidden")
        self.texto_accion = self.canvas.create_text(
            170, 462, text="", width=300, justify="center",
            font=("Arial", 16, "bold"), fill=COLOR_TEXTO,
            tags="caja_accion", state="hidden")

    def crear_botones(self):
        self.botones = []

        b_comer, w, h = self.crear_boton("Comer", "btn_comer",
                                         self.mostrar_comidas)
        y_fila = ALTO - h - 10
        self.canvas.create_window(15, y_fila, window=b_comer, anchor="nw",
                                  tags="botones_accion")
        self.botones.append(b_comer)
        x = 15 + w + 10

        # Botón Guardar: debajo del cuadro de datos (no se oculta con los demás)
        b_guardar, _, _ = self.crear_boton(
            "Guardar", "btn_guardar",
            lambda: self.ejecutar(lambda: self.yoshi.guardar(ARCHIVO),
                                  "Partida guardada"),
            ancho_texto=10)
        self.canvas.create_window(680, 135, window=b_guardar,
                                  tags="boton_guardar")
        self.botones.append(b_guardar)

        # (texto del botón, método, texto del cuadro, texto si lo rechaza)
        acciones = [("Dormir", self.yoshi.dormir, "Durmiendo...", "No tiene sueño"),
                    ("Jugar", self.yoshi.jugar, "Jugando...", None),
                    ("Curar", self.yoshi.curar, "Curando...", None),
                    ("Habilidad", self.yoshi.habilidad, None, None)]
        for texto, metodo, msg, rechazo in acciones:
            boton, bw, bh = self.crear_boton(
                texto, f"btn_{texto.lower()}",
                lambda m=metodo, t=msg, r=rechazo: self.ejecutar(m, t, r))
            etiquetas = ("botones_accion", "boton_habilidad") \
                if texto == "Habilidad" else ("botones_accion",)
            self.canvas.create_window(x, ALTO - bh - 10, window=boton,
                                      anchor="nw", tags=etiquetas)
            self.botones.append(boton)
            x += bw + 10

        self.ids_comidas = []
        for i, comida in enumerate(["Manzana", "Taco", "Hamburguesa"]):
            b, bw, bh = self.crear_boton(
                comida, f"btn_{comida.lower()}",
                lambda c=comida: self.comer(c), ancho_texto=11)
            wid = self.canvas.create_window(15, y_fila - (bh + 5) * (i + 1),
                                            window=b, anchor="nw",
                                            state="hidden")
            self.ids_comidas.append(wid)
            self.botones.append(b)

    def capturar(self, funcion):
        """Ejecuta la función y devuelve lo que habría impreso."""
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            funcion()
        lineas = [l.strip() for l in buffer.getvalue().splitlines() if l.strip()]
        return " ".join(lineas)

    def mostrar_accion(self, texto, dormir=False, habilidad=False):
        self.ocultar_comidas()
        self.canvas.itemconfig(self.texto_accion, text=texto)
        self.canvas.itemconfig("caja_accion", state="normal")
        self.canvas.itemconfig("botones_accion", state="hidden")
        if self.after_accion:
            self.root.after_cancel(self.after_accion)

        duracion = TIEMPO_ACCION
        if dormir:
            duracion = TIEMPO_DORMIR
            self.durmiendo = True
            self.canvas.itemconfig("boton_guardar", state="hidden")
            self.cambiar_fondo("fondo_noche")
            self.canvas.delete("yoshi_dibujo")
            self.dibujar_yoshi()
        elif habilidad:
            self.usando_habilidad = True
            self.canvas.delete("yoshi_dibujo")
            self.dibujar_yoshi()
        self.after_accion = self.root.after(duracion, self.terminar_accion)

    def terminar_accion(self):
        self.after_accion = None
        cambio = self.durmiendo or self.usando_habilidad
        if self.durmiendo:
            self.durmiendo = False
            self.cambiar_fondo("fondo_dia")
            self.canvas.itemconfig("boton_guardar", state="normal")
        self.usando_habilidad = False
        if cambio:
            self.canvas.delete("yoshi_dibujo")
            self.dibujar_yoshi()
        self.canvas.itemconfig("caja_accion", state="hidden")
        self.canvas.itemconfig("botones_accion", state="normal")
        self.actualizar_habilidad()
        if self.yoshi.vivo and random.random() < PROB_SONIDO:
            self.sonido_yoshi()

    def sonido_yoshi(self):
        texto = self.capturar(self.yoshi.sonido)
        self.canvas.delete("globo_sonido")
        self.canvas.create_text(ANCHO // 2, 70, text=texto,
                                font=("Arial", 22, "bold"), fill=COLOR_TEXTO,
                                tags="globo_sonido")
        self.root.after(TIEMPO_GLOBO,
                        lambda: self.canvas.delete("globo_sonido"))
        self.reproducir_audio()

    def reproducir_audio(self):
        ruta = None
        for ext in (".wav", ".ogg", ".mp3"):
            candidata = os.path.join(CARPETA_SONIDO, NOMBRE_SONIDO + ext)
            if os.path.exists(candidata):
                ruta = candidata
                break
        if ruta is None:
            return
        try:                               # pygame: wav, ogg y mp3
            import pygame
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            pygame.mixer.music.load(ruta)
            pygame.mixer.music.play()
            return
        except Exception:
            pass
        try:                               # sin pygame: solo .wav en Windows
            import winsound
            if ruta.endswith(".wav"):
                winsound.PlaySound(ruta, winsound.SND_FILENAME |
                                   winsound.SND_ASYNC)
        except Exception:
            pass

    def actualizar_habilidad(self):
        # El botón solo existe cuando es Adulto y no hay un mensaje en pantalla
        if self.after_accion is not None or not self.yoshi.vivo:
            return
        estado = "normal" if self.yoshi.etapa == "Adulto" else "hidden"
        self.canvas.itemconfig("boton_habilidad", state=estado)

    def ejecutar(self, accion, texto=None, rechazo=None):
        if not self.yoshi.vivo or self.durmiendo or self.usando_habilidad:
            return
        es_dormir = accion == self.yoshi.dormir
        es_habilidad = accion == self.yoshi.habilidad
        salida = self.capturar(accion)
        if rechazo and "aún no" in salida:
            texto = rechazo
            es_dormir = False
        elif texto is None:
            texto = salida
        if texto:
            self.mostrar_accion(texto, dormir=es_dormir,
                                habilidad=es_habilidad)
        self.actualizar_pantalla()

    def mostrar_comidas(self):
        if not self.yoshi.vivo:
            return
        visible = self.canvas.itemcget(self.ids_comidas[0], "state") == "normal"
        for wid in self.ids_comidas:
            self.canvas.itemconfig(wid, state="hidden" if visible else "normal")

    def ocultar_comidas(self):
        for wid in self.ids_comidas:
            self.canvas.itemconfig(wid, state="hidden")

    def comer(self, comida):
        if not self.yoshi.vivo:
            return
        salida = self.capturar(lambda: self.yoshi.comer(comida))
        if "aún no" in salida:
            self.mostrar_accion("No tiene hambre")
        else:
            self.mostrar_accion(f"Comiendo {comida.lower()}...")
        self.actualizar_pantalla()

    def tick(self):
        if not self.yoshi.vivo:
            return
        self.yoshi.pasar_tiempo()
        self.actualizar_pantalla()
        if self.yoshi.vivo:
            self.root.after(INTERVALO, self.tick)

    def actualizar_pantalla(self):
        if self.yoshi.etapa != self.etapa_dibujada:
            self.canvas.delete("yoshi_dibujo")
            self.dibujar_yoshi()

        self.actualizar_habilidad()

        for atributo, barra in self.barras.items():
            valor = max(0, min(100, getattr(self.yoshi, atributo)))
            x1, y1, x2, y2 = self.canvas.coords(barra)
            self.canvas.coords(barra, x1, y1, 50 + 135 * valor / 100, y2)

        if MOSTRAR_CRECIMIENTO:
            if self.yoshi.etapa == "Adulto":
                self.canvas.itemconfig("barra_crecer", state="hidden")
            else:
                meta = getattr(self.yoshi, "META_CRECER", META_CRECIMIENTO)
                progreso = min(meta, self.yoshi.crecer) / meta
                x1, y1, x2, y2 = self.canvas.coords(self.barra_crecer)
                self.canvas.coords(self.barra_crecer, 50, y1,
                                   50 + 135 * progreso, y2)

        genero = "Macho" if self.yoshi.genero == 0 else "Hembra"
        self.canvas.itemconfig(
            self.texto_datos,
            text=f"{self.yoshi.nombre}\n{self.yoshi.etapa} · {genero}\n"
                 f"Yoshi {self.yoshi.color}")

        estado = "normal" if self.yoshi.vivo else "disabled"
        for boton in self.botones:
            boton.config(state=estado)

        # Avisos del Yoshi (por ejemplo, evolución); esperan si está durmiendo
        if self.yoshi.aviso and not self.durmiendo:
            self.mostrar_accion(self.yoshi.aviso)
            self.yoshi.aviso = ""

        if not self.yoshi.vivo and not self.juego_terminado:
            self.juego_terminado = True
            borrar_partida()
            self.pantalla_muerte()
            
    def pantalla_muerte(self):
        if self.after_accion:
            self.root.after_cancel(self.after_accion)
            self.after_accion = None
        self.durmiendo = False
        self.usando_habilidad = False
        self.ocultar_comidas()
        self.canvas.itemconfig("botones_accion", state="hidden")
        self.canvas.itemconfig("boton_guardar", state="hidden")

        self.canvas.delete("yoshi_dibujo")
        self.dibujar_yoshi()

        self.canvas.itemconfig(self.texto_accion,
                               text=f"{self.yoshi.nombre} ha muerto...")
        self.canvas.itemconfig("caja_accion", state="normal")

        boton = tk.Button(self.root, text="Nuevo Yoshi", width=14,
                          font=("Arial", 12, "bold"), command=self.nuevo_yoshi)
        self.canvas.create_window(ANCHO // 2, 405, window=boton)

    def nuevo_yoshi(self):
        self.yoshi = None
        self.color_elegido = None
        self.juego_terminado = False
        self.en_juego = False
        self.after_accion = None
        self.durmiendo = False
        self.usando_habilidad = False
        self.pantalla_elegir_huevo()

    def cerrar(self):
        if self.en_juego and self.yoshi.vivo:
            r = messagebox.askyesnocancel("Salir", "¿Guardar antes de salir?")
            if r is None:                # Cancelar: no cierra
                return
            if r:
                self.yoshi.guardar(ARCHIVO)
        self.root.destroy()


def iniciar():
    root = tk.Tk()
    root.title("TamaYoshi")
    root.resizable(False, False)
    app = AppYoshi(root)
    root.protocol("WM_DELETE_WINDOW", app.cerrar)
    root.mainloop()


if __name__ == "__main__":
    iniciar()